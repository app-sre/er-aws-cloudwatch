variable "description" {
  type    = string
  default = "app-interface created Cloudwatch log group"
}

variable "es_identifier" {
  type        = string
  default     = null
  description = "Identifier of an existing elasticsearch. It will create a AWS lambda to stream logs to elasticsearch service"
}

variable "filter_pattern" {
  type        = string
  default     = ""
  description = "filter pattern for log data. Only works with streaming logs to elasticsearch"
}

variable "handler" {
  type    = string
  default = "index.handler"
}

variable "identifier" {
  type        = string
  description = "The resource identifier"
}

variable "lambda_file_path" {
  type        = string
  default     = "logs_to_es.zip"
  description = "Path of data.archive_file output file to reference in lambda function"
}

variable "memory_size" {
  type    = number
  default = 128
}

variable "output_resource_name" {
  type    = string
  default = null
}

variable "region" {
  type        = string
  default     = "us-east-1"
  description = "The region where the cloudwatch log group and supporting resources will be created"
}

variable "release_url" {
  type    = string
  default = null
}

variable "retention_in_days" {
  type        = number
  description = "Number of days to retain log events in the log group"
}

variable "runtime" {
  type    = string
  default = "nodejs18.x"
}

variable "tags" {
  type    = map(string)
  default = {}
}

variable "timeout" {
  type    = number
  default = 30
}

variable "should_import_lambda_log_group" {
  type        = bool
  default     = false
  description = "Whether to import existing lambda log group (updated by pre_plan hook)"
}
