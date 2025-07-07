# terraform/providers.tf
# ��������� ���������� ��� Google Cloud

provider "google" {}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}