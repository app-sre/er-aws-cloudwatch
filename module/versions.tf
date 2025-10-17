terraform {
  required_version = "1.6.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.17.0"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.7.1"
    }
  }
}