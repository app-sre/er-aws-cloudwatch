# Variables used by App-Interface. Not part of the resources definition.
variable "identifier" {
  description = "The resource identifier"
  type        = string
}

variable "region" {
  description = "The region where the cloudwatch log group and supporting resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "es_identifier" {
  description = "Identifier of an existing elasticsearch. It will create a AWS lambda to stream logs to elasticsearch service"
  type        = string
  default     = null
}

variable "lambda_file_path" {
  description = "Path for lambda repo downloaded from api.github.com for target lambda repo"
  type        = string
  default     = "/tmp/1.0.4-LogsToElasticsearch.zip"
}

# Variables directly used by resources
## aws_cloudwatch_log_group
variable "retention_in_days" {
  description = "Number of days to retain log events in the log group"
  type        = number
}

## aws_lambda_function
variable "runtime" {
  type    = string
  default = "nodejs18.x"
}

variable "timeout" {
  type    = number
  default = 30
}

variable "handler" {
  type    = string
  default = "index.handler"
}

variable "memory_size" {
  type    = number
  default = 128
}

## aws_cloudwatch_log_subscription_filter
variable "filter_pattern" {
  description = "filter pattern for log data. Only works with streaming logs to elasticsearch"
  type        = string
  default     = ""
}

## shared
variable "tags" {
  type = map(string)
}