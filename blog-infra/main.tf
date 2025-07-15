resource "google_container_cluster" "primary" {
  name     = "blog-gke"
  location = var.zone

  initial_node_count = 1

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_sql_database_instance" "blog" {
  name             = "blog-db"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # минимальный, для теста
    ip_configuration {
      # Для теста можно включить авторизацию по паролю и публичный IP
      ipv4_enabled    = true
      # authorized_networks = [] # Можно добавить свой IP для доступа
    }
  }
}

resource "google_sql_user" "blog" {
  name     = "bloguser"
  instance = google_sql_database_instance.blog.name
  password = "blogpassword" # придумай сложный пароль!
}

resource "google_sql_database" "blog" {
  name     = "blogdb"
  instance = google_sql_database_instance.blog.name
}