from typing import Any

from external_resources_io.input import AppInterfaceProvision
from pydantic import BaseModel, Field


class CloudwatchData(BaseModel):
    """Data model for AWS Cloudwatch"""

    # app-interface
    description: str = Field(default="app-interface created Cloudwatch log group")
    region: str
    identifier: str
    output_resource_name: str | None = None
    es_identifier: str | None = None
    release_url: str | None = None
    tags: dict[str, Any] | None = None

    # aws_cloudwatch_log_group
    retention_in_days: int

    # aws_lambda_function
    handler: str | None = None
    memory_size: int | None = None
    runtime: str | None = None
    timeout: int | None = None

    # aws_cloudwatch_log_subscription_filter
    filter_pattern: str | None = None


class AppInterfaceInput(BaseModel):
    """Input model for AWS Cloudwatch"""

    data: CloudwatchData
    provision: AppInterfaceProvision
