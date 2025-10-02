#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Console Application

Консольное приложение для анализа продаж кофе.
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

def main():
    """Главная функция консольного приложения."""
    # Настройка логирования
    logger = setup_logger()
    logger.info("Запуск консольного приложения")
    
    try:
        # Подключение к базе данных
        with DatabaseConnector() as db:
            if not db.test_connection():
                print("Ошибка подключения к базе данных!")
                return 1
            
            print("✅ Подключение к базе данных успешно!")
            
            # Создание анализатора
            analyzer = CoffeeAnalysis(db)
            
            # Пример анализа
            print("\n📊 Анализ продаж кофе...")
            
            # Получение статистики
            stats = analyzer.get_sales_statistics()
            print(f"Всего продаж: {stats['total_sales']}")
            print(f"Всего чашек: {stats['total_cups']}")
            print(f"Всего килограммов: {stats['total_weight']:.2f}")
            
            print("\n✅ Анализ завершен успешно!")
            
    except Exception as e:
        logger.error(f"Ошибка в консольном приложении: {e}")
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

