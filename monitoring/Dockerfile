FROM grafana/grafana:9.5.3

# Копирование файлов конфигурации (если они есть)
COPY grafana-dashboard.json /etc/grafana/provisioning/dashboards/default.json

# Устанавливаем плагины (опционально)
# RUN grafana-cli plugins install <plugin-name>

# Копирование конфигурационных файлов (если требуется)
# COPY grafana.ini /etc/grafana/grafana.ini
