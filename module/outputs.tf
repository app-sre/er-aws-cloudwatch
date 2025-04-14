output "log_group_name" {
  value = aws_cloudwatch_log_group.this.name
}

output "aws_region" {
  value = var.region
}