#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Test Application

Тестирование основных функций приложения.
"""

import sys
import os
from pathlib import Path

# Добавляем src в путь для импортов
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.database_connector import DatabaseConnector
from src.coffee_analysis import CoffeeAnalysis
from src.logger_config import setup_logger

def test_database_connection():
    """Тест подключения к базе данных."""
    print("🔌 Тестирование подключения к базе данных...")
    
    try:
        with DatabaseConnector() as db:
            if db.test_connection():
                print("✅ Подключение к базе данных успешно!")
                return True
            else:
                print("❌ Ошибка подключения к базе данных!")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_data_retrieval():
    """Тест получения данных."""
    print("\n📊 Тестирование получения данных...")
    
    try:
        with DatabaseConnector() as db:
            # Тест получения магазинов
            stores = db.get_stores_info()
            print(f"✅ Получено магазинов: {len(stores)}")
            
            # Тест получения данных о продажах
            sales_data = db.get_coffee_sales_with_packages(
                start_date='2025-09-29',
                end_date='2025-09-30'
            )
            print(f"✅ Получено записей о продажах: {len(sales_data)}")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_analysis():
    """Тест анализа данных."""
    print("\n🔍 Тестирование анализа данных...")
    
    try:
        with DatabaseConnector() as db:
            analyzer = CoffeeAnalysis(db)
            
            # Тест статистики
            stats = analyzer.get_sales_statistics()
            print(f"✅ Статистика получена: {stats}")
            
            return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Главная функция тестирования."""
    print("🧪 Запуск тестов приложения...")
    
    # Настройка логирования
    logger = setup_logger()
    logger.info("Запуск тестов приложения")
    
    tests = [
        test_database_connection,
        test_data_retrieval,
        test_analysis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📈 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
        return 0
    else:
        print("⚠️ Некоторые тесты не пройдены!")
        return 1

if __name__ == "__main__":
    sys.exit(main())

