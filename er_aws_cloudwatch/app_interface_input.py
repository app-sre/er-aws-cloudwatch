from external_resources_io.input import AppInterfaceProvision
from pydantic import BaseModel, Field


class CloudwatchData(BaseModel):
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
    """Input model for AWS Cloudwatch"""

    data: CloudwatchData
    provision: AppInterfaceProvision
