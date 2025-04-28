import pytest
from external_resources_io.input import parse_model

from er_aws_cloudwatch.app_interface_input import AppInterfaceInput


@pytest.fixture
def raw_input_data() -> dict:
    """Fixture to provide test data for the AppInterfaceInput."""
    return {
        "data": {
            "retention_in_days": 3653,
            "runtime": "nodejs18.x",
            "timeout": 60,
            "handler": "index.handler",
            "memory_size": 128,
            "identifier": "cloudwatch-example-es-01",
            "es_identifier": "app-int-example-01-es1",
            "output_resource_name": "cloudwatch-example-es-01",
            "tags": {
                "managed_by_integration": "external_resources",
                "cluster": "appint-ex-01",
                "namespace": "example-cloudwatch-01",
                "environment": "production",
                "app": "cloudwatch-example",
            },
            "default_tags": [{"tags": {"app": "app-sre-infra"}}],
            "region": "us-east-1",
        },
        "provision": {
            "provision_provider": "aws",
            "provisioner": "app-int-example-01",
            "provider": "cloudwatch",
            "identifier": "cloudwatch-example-es-01",
            "target_cluster": "appint-ex-01",
            "target_namespace": "example-cloudwatch-01",
            "target_secret_name": "cloudwatch-example-es-01",
            "module_provision_data": {
                "tf_state_bucket": "external-resources-terraform-state-dev",
                "tf_state_region": "us-east-1",
                "tf_state_dynamodb_table": "external-resources-terraform-lock",
                "tf_state_key": "aws/app-int-example-01/cloudwatch/cloudwatch-example-es-01/terraform.tfstate",
            },
        },
    }


@pytest.fixture
def ai_input(raw_input_data: dict) -> AppInterfaceInput:
    """Fixture to provide the AppInterfaceInput."""
    return parse_model(AppInterfaceInput, raw_input_data)
