# terraform/variables.tf
# Определяем переменные для нашей конфигурации

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "region" {
  description = "The region to deploy resources in"
  type        = string
  default     = "europe-north1"
}

variable "zone" {
  description = "The zone to deploy the VM in"
  type        = string
  default     = "europe-north1-c"
}

variable "duckdns_token" {
  description = "The token for DuckDNS API, needed for the update script"
  type        = string
  sensitive   = true # Скрывает значение токена в логах
}