provider "aws" {
  region = var.region

  default_tags {
    tags = var.tags
  }
}

provider "archive" {}

resource "aws_cloudwatch_log_group" "this" {
  name              = var.identifier
  retention_in_days = var.retention_in_days
  tags              = var.tags
}

resource "aws_iam_user" "this" {
  name       = var.identifier
  tags       = var.tags
  depends_on = [aws_cloudwatch_log_group.this]
}

resource "aws_iam_access_key" "this" {
  user = aws_iam_user.this.name
}

resource "aws_iam_policy" "this" {
  name = var.identifier
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:DescribeLogStreams",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "${aws_cloudwatch_log_group.this.arn}:*"
      },
      {
        Effect   = "Allow",
        Action   = ["logs:DescribeLogGroups"],
        Resource = "*"
      }
    ]
  })
  tags       = var.tags
  depends_on = [aws_iam_user.this]
}

resource "aws_iam_user_policy_attachment" "this" {
  user       = aws_iam_user.this.name
  policy_arn = aws_iam_policy.this.arn
  depends_on = [aws_iam_user.this, aws_iam_policy.this]
}

# All proceeding resources are optional and support streaming to elasticsearch
# All resources are enabled by specifying es_identifier

data "aws_elasticsearch_domain" "this" {
  count = var.es_identifier != null ? 1 : 0

  domain_name = var.es_identifier
}

resource "aws_iam_role" "this" {
  count = var.es_identifier != null ? 1 : 0

  name = "${var.identifier}-lambda-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "this" {
  count = var.es_identifier != null ? 1 : 0

  name = "${var.identifier}-lambda-execution-policy"
  role = aws_iam_role.this[0].id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ],
        Resource = "*"
      },
      {
        Effect   = "Allow",
        Action   = "es:*",
        Resource = "arn:aws:es:*"
      }
    ]
  })
}

data "archive_file" "this" {
  type        = "zip"
  source_file = "index.js"
  output_path = var.lambda_file_path
}

resource "aws_lambda_function" "this" {
  count = var.es_identifier != null ? 1 : 0

  filename         = var.lambda_file_path
  source_code_hash = data.archive_file.this.output_base64sha256
  function_name    = "${var.identifier}-lambda"
  handler          = var.handler
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  role             = aws_iam_role.this[0].arn

  vpc_config {
    subnet_ids         = data.aws_elasticsearch_domain.this[0].vpc_options[0].subnet_ids
    security_group_ids = data.aws_elasticsearch_domain.this[0].vpc_options[0].security_group_ids
  }

  environment {
    variables = {
      es_endpoint = data.aws_elasticsearch_domain.this[0].endpoint
    }
  }
  tags = var.tags
}

resource "aws_lambda_permission" "this" {
  count = var.es_identifier != null ? 1 : 0

  statement_id  = "cloudwatch_allow"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this[0].arn
  principal     = "logs.amazonaws.com"
  source_arn    = "${aws_cloudwatch_log_group.this.arn}:*"
}

resource "aws_cloudwatch_log_subscription_filter" "this" {
  count = var.es_identifier != null ? 1 : 0

  name            = aws_lambda_function.this[0].function_name
  log_group_name  = aws_cloudwatch_log_group.this.name
  destination_arn = aws_lambda_function.this[0].arn
  filter_pattern  = var.filter_pattern
  depends_on      = [aws_cloudwatch_log_group.this]
}

# Import existing lambda log group if it exists and is unmanaged
import {
  for_each = var.should_import_lambda_log_group ? toset(["import"]) : []
  to       = aws_cloudwatch_log_group.lambda_logs[0]
  id       = "/aws/lambda/${var.identifier}-lambda"
}

# Lambda log group resource
resource "aws_cloudwatch_log_group" "lambda_logs" {
  count = var.es_identifier != null ? 1 : 0

  name              = "/aws/lambda/${var.identifier}-lambda"
  retention_in_days = var.retention_in_days
  tags              = var.tags
}
