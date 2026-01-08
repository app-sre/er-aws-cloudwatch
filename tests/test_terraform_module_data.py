"""Tests for the TerraformModuleData class."""

from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest

from er_aws_cloudwatch.app_interface_input import AppInterfaceInput, TerraformModuleData


@pytest.fixture
def mock_boto3_client() -> Iterator[Mock]:
    """Patch boto3.client"""
    with patch("er_aws_cloudwatch.app_interface_input.boto3.client") as m:
        yield m


@pytest.fixture
def mock_logs_client() -> Mock:
    """Create a mock CloudWatch Logs client."""
    client = Mock()
    client.describe_log_groups.return_value = {"logGroups": []}
    client.list_tags_log_group.return_value = {"tags": {}}
    return client


class TestTerraformModuleData:
    """Test cases for TerraformModuleData computed fields."""

    def test_should_import_lambda_log_group_no_es_identifier(  # noqa: PLR6301
        self, ai_input: AppInterfaceInput, mock_boto3_client: Mock
    ) -> None:
        """Test that function returns False when es_identifier is None."""
        ai_input.data.es_identifier = None
        tf_data = TerraformModuleData(ai_input=ai_input)
        result = tf_data.should_import_lambda_log_group
        assert result is False
        mock_boto3_client.assert_not_called()

    def test_should_import_lambda_log_group_log_group_not_found(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test that function returns False when log group doesn't exist."""
        mock_boto3_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {"logGroups": []}

        tf_data = TerraformModuleData(ai_input=ai_input)
        result = tf_data.should_import_lambda_log_group

        assert result is False
        mock_boto3_client.assert_called_once_with(
            "logs", region_name=ai_input.data.region
        )
        mock_logs_client.describe_log_groups.assert_called_once_with(
            logGroupNamePrefix="/aws/lambda/cloudwatch-example-es-01-lambda"
        )
        mock_logs_client.list_tags_log_group.assert_not_called()

    def test_should_import_lambda_log_group_unmanaged_returns_true(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test that function returns True when log group exists but is unmanaged."""
        mock_boto3_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {
            "logGroups": [
                {
                    "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                    "creationTime": 1234567890.0,
                }
            ]
        }
        # No managed_by_integration tag (unmanaged)
        mock_logs_client.list_tags_log_group.return_value = {
            "tags": {
                "environment": "production",
                "app": "some-other-app",
            }
        }

        tf_data = TerraformModuleData(ai_input=ai_input)
        result = tf_data.should_import_lambda_log_group

        assert result is True
        mock_logs_client.describe_log_groups.assert_called_once()
        mock_logs_client.list_tags_log_group.assert_called_once_with(
            logGroupName="/aws/lambda/cloudwatch-example-es-01-lambda"
        )

    def test_should_import_lambda_log_group_managed_returns_false(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test that function returns False when log group exists and is managed."""
        mock_boto3_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {
            "logGroups": [
                {
                    "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                    "creationTime": 1234567890.0,
                }
            ]
        }
        mock_logs_client.list_tags_log_group.return_value = {
            "tags": {
                "managed_by_integration": "external_resources",
                "environment": "production",
            }
        }

        tf_data = TerraformModuleData(ai_input=ai_input)
        result = tf_data.should_import_lambda_log_group

        assert result is False
        mock_logs_client.describe_log_groups.assert_called_once()
        mock_logs_client.list_tags_log_group.assert_called_once()
