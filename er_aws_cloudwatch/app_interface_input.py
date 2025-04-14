import os
from pathlib import Path
from typing import Any

import requests
from external_resources_io.input import AppInterfaceProvision
from pydantic import BaseModel

GH_BASE_URL = os.environ.get("GITHUB_API", "https://api.github.com")


class CloudwatchData(BaseModel):
    """Data model for AWS Cloudwatch"""

    # app-interface
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

    def download_es_lambda(self) -> None:
        """Responsible for downloading lambda repo and setting attr to use tf vars"""
        if self.es_identifier:
            headers = {"Authorization": "token " + os.environ.get("GITHUB_TOKEN")}
            r = requests.get(f"{GH_BASE_URL}/{self.release_url}", headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()
            # ex: https://api.github.com/repos/app-sre/logs-to-elasticsearch-lambda/releases/latest
            zip_url = data["assets"][0]["browser_download_url"]
            zip_file = f"/tmp/{data['tag_name']}-{data['assets'][0]['name']}"
            r = requests.get(zip_url, timeout=60)
            r.raise_for_status()
            Path(zip_file).write_bytes(r.content)
            self.lambda_file_path = zip_file


class AppInterfaceInput(BaseModel):
    """Input model for AWS Cloudwatch"""

    data: CloudwatchData
    provision: AppInterfaceProvision
