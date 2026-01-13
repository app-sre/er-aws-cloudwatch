import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from external_resources_io.input import AppInterfaceProvision
from pydantic import BaseModel, Field


class Cloudwatch(BaseModel):
    """Data model for AWS Cloudwatch"""

    # app-interface
    description: str = Field(default="app-interface created Cloudwatch log group")
    region: str = Field(
        "us-east-1",
        description="The region where the cloudwatch log group and supporting resources will be created",
    )
    identifier: str = Field(description="The resource identifier")
    output_resource_name: str | None = None
    es_identifier: str | None = Field(
        None,
        description="Identifier of an existing elasticsearch. It will create a AWS lambda to stream logs to elasticsearch service",
    )
    release_url: str | None = None
    tags: dict[str, str] = {}

    # aws_cloudwatch_log_group
    retention_in_days: int = Field(
        description="Number of days to retain log events in the log group"
    )

    # aws_lambda_function
    handler: str | None = "index.handler"
    memory_size: int | None = 128
    runtime: str | None = "nodejs18.x"
    timeout: int | None = 30
    lambda_file_path: str | None = Field(
        "logs_to_es.zip",
        description="Path of data.archive_file output file to reference in lambda function",
    )

    # aws_cloudwatch_log_subscription_filter
    filter_pattern: str | None = Field(
        "",
        description="filter pattern for log data. Only works with streaming logs to elasticsearch",
    )

    # computed fields for module
    import_log_group_lambda_function_names: list[str] | None = Field(
        default=None,
        description="Additional log groups associated with lambda to manage",
    )


class AppInterfaceInput(BaseModel):
    """Input model class"""

    data: Cloudwatch
    provision: AppInterfaceProvision


def log_group_exists(function_name: str, region: str) -> bool:
    log_group_name = f"/aws/lambda/{function_name}"
    logger = logging.getLogger(__name__)
    try:
        client = boto3.client("logs", region_name=region)
        response = client.describe_log_groups(logGroupNamePrefix=log_group_name)
        log_groups = response.get("logGroups", [])
        # Ensure exact match in case logGroupNamePrefix found additional groups
        target_group = next(
            (lg for lg in log_groups if lg.get("logGroupName") == log_group_name),
            None,
        )
        if not target_group:
            logger.debug(f"Existing log group {log_group_name} not found.")
            return False
        return True  # noqa: TRY300
    except (ClientError, BotoCoreError) as e:
        logger.warning(f"Failed to check log group {log_group_name}: {e}.")
        raise


def process_input_data(data: Cloudwatch) -> Cloudwatch:
    lambda_function_names = [f"{data.identifier}-lambda"] if data.es_identifier else []
    import_log_group_lambda_function_names = [
        name for name in lambda_function_names if log_group_exists(name, data.region)
    ]
    return Cloudwatch.model_validate(
        data.model_dump()
        | {
            "import_log_group_lambda_function_names": import_log_group_lambda_function_names
        }
    )
