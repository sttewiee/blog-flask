#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""
import os
from app import create_app, db

def init_database():
    """Инициализация базы данных"""
    app = create_app()
    
    with app.app_context():
        try:
            # Создаем все таблицы
            db.create_all()
            print("✅ База данных инициализирована успешно")
            
            # Проверяем, что таблицы созданы
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Созданные таблицы: {tables}")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            raise

if __name__ == '__main__':
    init_database()
