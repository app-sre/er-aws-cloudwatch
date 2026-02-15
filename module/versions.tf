terraform {
  required_version = "1.13.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.32.1"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.7.1"
    }
  }
}