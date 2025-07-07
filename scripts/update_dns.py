# scripts/update_dns.py
import os
import sys
import requests

def update_duckdns(domain, token, ip):
    """
    Отправляет запрос на API DuckDNS для обновления IP-адреса домена.
    """
    print(f"Attempting to update domain '{domain}' to IP '{ip}'...")
    
    url = "https://www.duckdns.org/update"
    params = {
        "domains": domain,
        "token": token,
        "ip": ip,
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Вызовет ошибку для статусов 4xx/5xx

        if response.text.strip() == "OK":
            print(f"SUCCESS: DuckDNS for '{domain}' was updated to '{ip}'.")
        else:
            # Ответ от DuckDNS не "OK", выводим его и завершаемся с ошибкой
            print(f"ERROR: DuckDNS update failed. Response from server: {response.text.strip()}")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"ERROR: An HTTP error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Скрипт ожидает, что переменные будут переданы через окружение
    # Terraform сделает это автоматически
    duckdns_domain = os.getenv("DUCKDNS_DOMAIN")
    duckdns_token = os.getenv("DUCKDNS_TOKEN")
    target_ip = os.getenv("TARGET_IP")

    if not all([duckdns_domain, duckdns_token, target_ip]):
        print("FATAL ERROR: Missing required environment variables (DUCKDNS_DOMAIN, DUCKDNS_TOKEN, TARGET_IP).")
        sys.exit(1)
        
    update_duckdns(duckdns_domain, duckdns_token, target_ip)
