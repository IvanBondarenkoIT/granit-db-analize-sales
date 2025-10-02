#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ОТЛАДКА КОЛОНОК - ПРОВЕРКА СТРУКТУРЫ ДАННЫХ
"""

import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_connector import DatabaseConnector

def debug_columns():
    """Отладка колонок"""
    print("=== ОТЛАДКА КОЛОНОК ===")
    
    try:
        with DatabaseConnector() as db:
            # Получаем данные
            sales_data = db.get_coffee_sales_with_packages(
                store_ids=[27, 43, 44, 46],
                start_date="2025-09-29",
                end_date="2025-09-30"
            )
            
            print(f"Получено записей: {len(sales_data)}")
            print(f"Колонки: {list(sales_data.columns)}")
            
            if not sales_data.empty:
                print("\nПервые 3 записи:")
                print(sales_data.head(3))
                
                print("\nТипы данных:")
                print(sales_data.dtypes)
                
                print("\nСтатистика:")
                print(sales_data.describe())
            
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_columns()
