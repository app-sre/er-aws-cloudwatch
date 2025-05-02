output "log_group_name" {
  value = aws_cloudwatch_log_group.this.name
}

output "aws_region" {
  value = var.region
}

output "aws_access_key_id" {
  value = aws_iam_access_key.this.id
}

output "aws_secret_access_key" {
  value     = aws_iam_access_key.this.secret
  sensitive = true
}
