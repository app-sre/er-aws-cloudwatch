#!/usr/bin/env python
import json
import logging
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from external_resources_io.config import Config
from external_resources_io.exit_status import EXIT_ERROR, EXIT_OK
from external_resources_io.input import parse_model, read_input_from_file
from external_resources_io.log import setup_logging
from mypy_boto3_logs.client import CloudWatchLogsClient
from pydantic import ValidationError

from er_aws_cloudwatch.app_interface_input import AppInterfaceInput

logger = logging.getLogger(__name__)


def check_lambda_log_group_import_needed(
    identifier: str, es_identifier: str | None, logs_client: CloudWatchLogsClient
) -> bool:
    """Determine if import needed"""
    if not es_identifier:
        return False

    log_group_name = f"/aws/lambda/{identifier}-lambda"
    try:
        response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
        log_groups = response.get("logGroups", [])
        # ensure exact match, in case logGroupNamePrefix found additional
        target_group = next(
            (lg for lg in log_groups if lg.get("logGroupName") == log_group_name), None
        )
        if not target_group:
            logger.debug(f"Existing log group {log_group_name} not found.")
            return False

        # Check tags to determine if it's managed by external_resources
        try:
            tags_response = logs_client.list_tags_log_group(logGroupName=log_group_name)
            tags = tags_response.get("tags", {})
            managed_by_tag = tags.get("managed_by_integration")

            should_import = managed_by_tag != "external_resources"
            if should_import:
                logger.info(
                    f"Log group {log_group_name} exists but not managed by external_resources "
                    f"(managed_by_integration={managed_by_tag}). Import needed."
                )
            else:
                logger.debug(
                    f"Log group {log_group_name} already managed by external_resources."
                )
            return should_import  # noqa: TRY300
        except (ClientError, BotoCoreError) as e:
            logger.error(f"Failed to get tags for {log_group_name}: {e}")  # noqa: TRY400
            raise
    except (ClientError, BotoCoreError) as e:
        logger.error(f"Failed to list log groups with prefix match: {e}")  # noqa: TRY400
        raise


def update_tf_vars_with_true_import_flag() -> None:
    """Updates terraform.tfvars.json with lambda import var set to True."""
    config = Config()
    output = Path(config.tf_vars_file)
    # Read existing vars (created by generate-tf-config)
    existing_vars = {}
    if output.exists():
        existing_vars = json.loads(output.read_text(encoding="utf-8"))
    existing_vars["should_import_lambda_log_group"] = True
    output.write_text(
        json.dumps(existing_vars),
        encoding="utf-8",
    )


def main() -> None:
    """Checks if optional lambda log group exists and imports if existing but not managed"""
    setup_logging()

    try:
        app_interface_input: AppInterfaceInput = parse_model(
            AppInterfaceInput, read_input_from_file
        )
        data = app_interface_input.data
        identifier = data.identifier
        es_id = data.es_identifier

        session = boto3.Session(region_name=data.region)
        logs_client = session.client("logs")
        should_import = check_lambda_log_group_import_needed(
            identifier=identifier, es_identifier=es_id, logs_client=logs_client
        )

        if should_import:
            update_tf_vars_with_true_import_flag()

        logger.info(f"Success: identifier={identifier}, should_import={should_import}")
        sys.exit(EXIT_OK)
    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")  # noqa: TRY400
        sys.exit(EXIT_ERROR)
    except (ClientError, BotoCoreError, IOError) as e:  # noqa: UP024
        logger.error(f"Operational error: {e}")  # noqa: TRY400
        sys.exit(EXIT_ERROR)
    except Exception:
        logger.exception("Error attempting to verify lambda log group state")
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    main()
