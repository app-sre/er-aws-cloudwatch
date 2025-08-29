terraform {
  required_version = "1.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.82.2"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "2.7.0"
    }
  }
}