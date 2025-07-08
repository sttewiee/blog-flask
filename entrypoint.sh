# �� ����� ��������� ������
nano entrypoint.sh
```������ � ���� ��������� ���. ���� ������ � ����� ����� ����� � ���� ���������.
```bash
#!/bin/sh
set -e

# 1. ����, ���� ���� ������ �� ������ ���������
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

# 2. ��������� �������� ���� ������
echo "Applying database migrations..."
flask db upgrade

# 3. ��������� �������� ������� (gunicorn)
exec "$@"