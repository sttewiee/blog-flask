# terraform/providers.tf
# ќбъ€вл€ем провайдера дл€ Google Cloud

provider "google" {}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}