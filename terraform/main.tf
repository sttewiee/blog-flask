# terraform/main.tf

# 1. Резервируем постоянный (статический) IP-адрес
resource "google_compute_address" "static_ip" {
  project = var.project_id
  name    = "blog-flask-static-ip"
  region  = var.region
}

# 2. Создаем виртуальную машину
resource "google_compute_instance" "blog_server" {
  project      = var.project_id
  zone         = var.zone
  name         = "blog-flask-server-terraform"
  machine_type = "e2-micro"
  tags         = ["http-server", "httpss-server"]

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

  # --- ИСПРАВЛЕННЫЙ БЛОК PROVISIONER ---
  # Блок connection вынесен на один уровень с provisioner
  connection {
    type        = "ssh"
    user        = "gcpa4607" # <-- Ваше имя пользователя
    private_key = file("~/.ssh/google_compute_engine")
    host        = self.network_interface[0].access_config[0].nat_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sleep 20",
      "sudo apt-get update",
      "sudo apt-get install -y docker.io docker-compose git",
      # Жестко прописываем ваше имя пользователя
      "sudo usermod -aG docker gcpa4607",
    ]
  }
}

# 3. Обновляем DNS с помощью нашего Python-скрипта
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

# 4. Выводим постоянный IP-адрес в консоль
output "static_instance_ip" {
  description = "The static external IP address of the VM instance"
  value       = google_compute_address.static_ip.address
}