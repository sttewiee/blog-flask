#!/usr/bin/env python3
"""
Скрипт для запуска тестов
"""
import os
import sys
import subprocess

def run_tests():
    """Запускает тесты с правильными переменными окружения"""
    # Устанавливаем переменные окружения для тестов
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test_secret_key'
    os.environ['FLASK_ENV'] = 'testing'
    
    # Запускаем pytest
    result = subprocess.run([
        sys.executable, '-m', 'pytest', 
        '-v', 
        '--cov=app', 
        '--cov-report=term-missing'
    ])
    
    return result.returncode

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code) 