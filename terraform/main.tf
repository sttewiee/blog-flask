# terraform/main.tf

# 1. Резервируем постоянный (статический) IP-адрес
resource "google_compute_address" "static_ip" {
  project = var.project_id
  name    = "blog-flask-static-ip"
  region  = var.region
}

# 2. Правило Firewall для разрешения SSH (порт 22)
# Необходимо, чтобы GitHub Actions мог подключиться к серверу для деплоя.
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

# 3. Правило Firewall для разрешения HTTP (порт 80)
# Необходимо, чтобы Let's Encrypt мог проверить домен.
resource "google_compute_firewall" "allow_http" {
  project = var.project_id
  name    = "allow-http-from-anywhere"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["80"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

# 4. Правило Firewall для разрешения HTTPS (порт 443)
# Для использования SSL сертификатов Let's Encrypt.
resource "google_compute_firewall" "allow_https" {
  project = var.project_id
  name    = "allow-https-from-anywhere"
  network = "default"
  allow {
    protocol = "tcp"
    ports    = ["443"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["https-server"]
}

# 5. Создаем виртуальную машину
resource "google_compute_instance" "blog_server" {
  project      = var.project_id
  zone         = var.zone
  name         = "blog-flask-server-terraform"
  machine_type = "e2-micro"
  
  # Используем теги, чтобы применить к ВМ наши правила Firewall
  tags         = ["http-server", "https-server", "ssh-server"]

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

  connection {
    type        = "ssh"
    user        = "gcpa4607"
    private_key = file("~/.ssh/google_compute_engine")  # Убедитесь, что путь к вашему ключу правильный
    host        = self.network_interface[0].access_config[0].nat_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sleep 20",  # Даем время на инициализацию машины
      "sudo apt-get update",
      "sudo apt-get install -y docker.io docker-compose git",
      "sudo usermod -aG docker gcpa4607",
    ]
  }
}

# 6. Обновляем DNS
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

# 7. Выводим IP-адрес
output "static_instance_ip" {
  description = "The static external IP address of the VM instance"
  value       = google_compute_address.static_ip.address
}
