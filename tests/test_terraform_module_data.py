"""Tests for the process_input_data function."""

from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest

from er_aws_cloudwatch.app_interface_input import (
    AppInterfaceInput,
    Cloudwatch,
    process_input_data,
)


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
    return client


class TestProcessInputData:
    """Test cases for process_input_data function."""

    def test_process_input_data_no_es_identifier(  # noqa: PLR6301
        self, ai_input: AppInterfaceInput, mock_boto3_client: Mock
    ) -> None:
        """Test that function returns empty list when es_identifier is None."""
        ai_input.data.es_identifier = None
        result = process_input_data(ai_input.data)
        assert result.import_log_group_lambda_function_names == []
        mock_boto3_client.assert_not_called()

    def test_process_input_data_log_group_not_found(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test that function returns empty list when log group doesn't exist."""
        mock_boto3_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {"logGroups": []}

        result = process_input_data(ai_input.data)

        assert result.import_log_group_lambda_function_names == []
        mock_boto3_client.assert_called_once_with(
            "logs", region_name=ai_input.data.region
        )
        mock_logs_client.describe_log_groups.assert_called_once_with(
            logGroupNamePrefix="/aws/lambda/cloudwatch-example-es-01-lambda"
        )

    def test_process_input_data_log_group_exists(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test that function includes function name when log group exists."""
        mock_boto3_client.return_value = mock_logs_client
        mock_logs_client.describe_log_groups.return_value = {
            "logGroups": [
                {
                    "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                    "creationTime": 1234567890.0,
                }
            ]
        }

        result = process_input_data(ai_input.data)

        assert result.import_log_group_lambda_function_names == [
            "cloudwatch-example-es-01-lambda"
        ]
        mock_logs_client.describe_log_groups.assert_called_once_with(
            logGroupNamePrefix="/aws/lambda/cloudwatch-example-es-01-lambda"
        )

    def test_process_input_data_multiple_scenarios(  # noqa: PLR6301
        self,
        ai_input: AppInterfaceInput,
        mock_boto3_client: Mock,
        mock_logs_client: Mock,
    ) -> None:
        """Test function behavior with various input scenarios."""
        mock_boto3_client.return_value = mock_logs_client

        # Test with existing log group
        mock_logs_client.describe_log_groups.return_value = {
            "logGroups": [
                {
                    "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                    "creationTime": 1234567890.0,
                }
            ]
        }

        result = process_input_data(ai_input.data)
        assert isinstance(result, Cloudwatch)
        assert result.import_log_group_lambda_function_names == [
            "cloudwatch-example-es-01-lambda"
        ]
        assert result.identifier == ai_input.data.identifier
        assert result.region == ai_input.data.region
