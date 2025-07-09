# terraform/main.tf

# 1. Резервируем постоянный (статический) IP-адрес
resource "google_compute_address" "static_ip" {
  project = var.project_id
  name    = "blog-flask-static-ip"
  region  = var.region
}

# 2. НОВЫЙ РЕСУРС: Правило Firewall для разрешения SSH
# Это правило разрешает входящий трафик на порт 22 с любого IP-адреса
# для всех виртуальных машин с тегом "ssh-server".
# Это необходимо, чтобы GitHub Actions мог подключиться к серверу для деплоя.
resource "google_compute_firewall" "allow_ssh" {
  project = var.project_id
  name    = "allow-ssh-from-anywhere"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-server"]
}


# 3. Создаем виртуальную машину
resource "google_compute_instance" "blog_server" {
  project      = var.project_id
  zone         = var.zone
  name         = "blog-flask-server-terraform"
  machine_type = "e2-micro"
  
  # ИЗМЕНЕНИЕ: Добавляем тег "ssh-server", чтобы применить правило Firewall
  tags         = ["http-server", "httpss-server", "ssh-server"]

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
    }
  }

  network_interface {
    network    = "default"
    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  # Блок connection для provisioner'а
  connection {
    type        = "ssh"
    user        = "gcpa4607" # <-- Ваше имя пользователя
    private_key = file("~/.ssh/google_compute_engine")
    host        = self.network_interface[0].access_config[0].nat_ip
  }

  # Provisioner для первоначальной настройки сервера
  provisioner "remote-exec" {
    inline = [
      "sleep 20", # Даем время на инициализацию системы после загрузки
      "sudo apt-get update",
      "sudo apt-get install -y docker.io docker-compose git",
      # Добавляем пользователя в группу docker, чтобы не использовать sudo для Docker
      "sudo usermod -aG docker gcpa4607",
    ]
  }
}

# 4. Обновляем DNS с помощью нашего Python-скрипта
resource "null_resource" "update_dns_via_python" {
  depends_on = [google_compute_address.static_ip]

  provisioner "local-exec" {
    command = "python3 ../scripts/update_dns.py"
    environment = {
      DUCKDNS_DOMAIN = "lapikoff"
      DUCKDNS_TOKEN  = var.duckdns_token
      TARGET_IP      = google_compute_address.static_ip.address
    }
  }
}

# 5. Выводим постоянный IP-адрес в консоль
output "static_instance_ip" {
  description = "The static external IP address of the VM instance"
  value       = google_compute_address.static_ip.address
}