from collections.abc import Iterator
from unittest.mock import Mock, patch

import pytest
from hooks.pre_plan import main

from er_aws_cloudwatch.app_interface_input import AppInterfaceInput


@pytest.fixture
def mock_read_input_from_file() -> Iterator[Mock]:
    """Patch read_input_from_file"""
    with patch("hooks.pre_plan.read_input_from_file") as m:
        yield m


@pytest.fixture
def mock_parse_model() -> Iterator[Mock]:
    """Patch parse_model"""
    with patch("hooks.pre_plan.parse_model") as m:
        yield m


@pytest.fixture
def mock_setup_logging() -> Iterator[Mock]:
    """Patch setup_logging"""
    with patch("hooks.pre_plan.setup_logging") as m:
        yield m


@pytest.fixture
def mock_boto3_session() -> Iterator[Mock]:
    """Patch boto3.Session"""
    with patch("hooks.pre_plan.boto3.Session") as m:
        yield m


@pytest.fixture
def mock_update_tf_vars() -> Iterator[Mock]:
    """Patch update_tf_vars_with_true_import_flag"""
    with patch("hooks.pre_plan.update_tf_vars_with_true_import_flag") as m:
        yield m


@pytest.fixture
def mock_logs_client() -> Mock:
    """Create a mock CloudWatch Logs client."""
    client = Mock()
    client.describe_log_groups.return_value = {"logGroups": []}
    client.list_tags_log_group.return_value = {"tags": {}}
    return client


def test_pre_plan_hook_no_es_identifier(  # noqa: PLR0913, PLR0917
    mock_read_input_from_file: Mock,
    mock_parse_model: Mock,
    mock_boto3_session: Mock,
    mock_update_tf_vars: Mock,
    mock_logs_client: Mock,
    raw_input_data: dict,
) -> None:
    """Test pre_plan hook when es_identifier is None (no import needed)."""
    input_data_no_es = raw_input_data.copy()
    input_data_no_es["data"]["es_identifier"] = None

    mock_read_input_from_file.return_value = input_data_no_es
    mock_parse_model.return_value.data.identifier = "test-identifier"
    mock_parse_model.return_value.data.es_identifier = None
    mock_parse_model.return_value.data.region = "us-east-1"
    mock_boto3_session.return_value.client.return_value = mock_logs_client

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 0
    mock_parse_model.assert_called_once()
    mock_boto3_session.assert_called_once_with(region_name="us-east-1")
    # Should not call AWS APIs or update tfvars when es_identifier is None
    mock_logs_client.describe_log_groups.assert_not_called()
    mock_update_tf_vars.assert_not_called()


def test_pre_plan_hook_log_group_not_found(  # noqa: PLR0913, PLR0917
    mock_read_input_from_file: Mock,
    mock_parse_model: Mock,
    mock_boto3_session: Mock,
    mock_update_tf_vars: Mock,
    mock_logs_client: Mock,
    ai_input: AppInterfaceInput,
) -> None:
    """Test pre_plan hook when log group doesn't exist (no import needed)."""
    mock_read_input_from_file.return_value = {}
    mock_parse_model.return_value = ai_input
    mock_boto3_session.return_value.client.return_value = mock_logs_client
    mock_logs_client.describe_log_groups.return_value = {"logGroups": []}

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 0
    mock_logs_client.describe_log_groups.assert_called_once()
    mock_logs_client.list_tags_log_group.assert_not_called()
    mock_update_tf_vars.assert_not_called()


def test_pre_plan_hook_log_group_unmanaged_import_needed(  # noqa: PLR0913, PLR0917
    mock_read_input_from_file: Mock,
    mock_parse_model: Mock,
    mock_boto3_session: Mock,
    mock_update_tf_vars: Mock,
    mock_logs_client: Mock,
    ai_input: AppInterfaceInput,
) -> None:
    """Test pre_plan hook when log group exists but is unmanaged (import needed)."""
    mock_read_input_from_file.return_value = {}
    mock_parse_model.return_value = ai_input
    mock_boto3_session.return_value.client.return_value = mock_logs_client

    # Log group exists
    mock_logs_client.describe_log_groups.return_value = {
        "logGroups": [
            {
                "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                "creationTime": 1234567890.0,
            }
        ]
    }
    # Log group not managed by external_resources
    mock_logs_client.list_tags_log_group.return_value = {
        "tags": {
            "environment": "production",
            "app": "some-other-app",
            "managed_by_integration": "aws_cloudwatch_log_retention",
        }
    }

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 0
    mock_logs_client.describe_log_groups.assert_called_once()
    mock_logs_client.list_tags_log_group.assert_called_once()
    mock_update_tf_vars.assert_called_once()


def test_pre_plan_hook_log_group_managed_no_import(  # noqa: PLR0913, PLR0917
    mock_read_input_from_file: Mock,
    mock_parse_model: Mock,
    mock_boto3_session: Mock,
    mock_update_tf_vars: Mock,
    mock_logs_client: Mock,
    ai_input: AppInterfaceInput,
) -> None:
    """Test pre_plan hook when log group exists and is managed (no import needed)."""
    mock_read_input_from_file.return_value = {}
    mock_parse_model.return_value = ai_input
    mock_boto3_session.return_value.client.return_value = mock_logs_client

    # Log group exists
    mock_logs_client.describe_log_groups.return_value = {
        "logGroups": [
            {
                "logGroupName": "/aws/lambda/cloudwatch-example-es-01-lambda",
                "creationTime": 1234567890.0,
            }
        ]
    }
    # Has managed_by_integration tag set to external_resources (managed)
    mock_logs_client.list_tags_log_group.return_value = {
        "tags": {
            "managed_by_integration": "external_resources",
            "environment": "production",
        }
    }

    with pytest.raises(SystemExit) as e:
        main()

    assert e.value.code == 0
    mock_logs_client.describe_log_groups.assert_called_once()
    mock_logs_client.list_tags_log_group.assert_called_once()
    mock_update_tf_vars.assert_not_called()
