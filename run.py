#!/usr/bin/env python3
"""
Скрипт для запуска Flask приложения
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Определяем режим на основе FLASK_ENV
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000) 