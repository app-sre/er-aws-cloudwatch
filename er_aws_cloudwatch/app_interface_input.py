import logging

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from external_resources_io.input import AppInterfaceProvision
from pydantic import BaseModel, Field, computed_field


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


class AppInterfaceInput(BaseModel):
    """Input model class"""

    data: Cloudwatch
    provision: AppInterfaceProvision


class TerraformModuleData(Cloudwatch):
    """Vars for the Terraform module"""

    def __init__(self, ai_input: AppInterfaceInput) -> None:
        # Initialize with all the data from ai_input.data
        super().__init__(**ai_input.data.model_dump())

    @computed_field
    def should_import_lambda_log_group(self) -> bool:
        """Determine if lambda log group needs to be imported"""
        logger = logging.getLogger(__name__)

        if not self.es_identifier:
            return False

        log_group_name = f"/aws/lambda/{self.identifier}-lambda"
        try:
            client = boto3.client("logs", region_name=self.region)
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

            tags_response = client.list_tags_log_group(logGroupName=log_group_name)
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
            logger.warning(f"Failed to check log group {log_group_name}: {e}.")
            raise
