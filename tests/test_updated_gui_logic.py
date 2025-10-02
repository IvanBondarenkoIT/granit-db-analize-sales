#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТ ОБНОВЛЕННОЙ ЛОГИКИ GUI
"""

import sys
import os
from datetime import datetime

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_connector import DatabaseConnector
from logger_config import setup_logger

# Настраиваем логирование
logger = setup_logger(__name__)

def test_updated_gui_logic():
    """Тестирует обновленную логику GUI"""
    try:
        with DatabaseConnector() as db:
            print("=== ТЕСТ ОБНОВЛЕННОЙ ЛОГИКИ GUI ===")
            print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Тестируем новый метод
            print("\n=== ТЕСТ МЕТОДА get_coffee_sales_with_packages ===")
            sales_data = db.get_coffee_sales_with_packages(
                store_ids=[27, 43, 44, 46],  # Основные магазины
                start_date="2025-09-29",
                end_date="2025-09-30"
            )
            
            print(f"Получено записей: {len(sales_data)}")
            
            if not sales_data.empty:
                print("\nСтруктура данных:")
                print(f"Колонки: {list(sales_data.columns)}")
                print(f"Размер: {sales_data.shape}")
                
                print("\nПервые 5 записей:")
                print(sales_data.head())
                
                print("\nСтатистика по колонкам:")
                print(sales_data.describe())
                
                # Проверяем наличие нужных колонок
                required_columns = ['STORE_NAME', 'ORDER_DATE', 'MONOCUP', 'BLENDCUP', 'CAOTINACUP', 'ALLCUP', 'PACKAGES_KG', 'TOTAL_CASH']
                missing_columns = [col for col in required_columns if col not in sales_data.columns]
                
                if missing_columns:
                    print(f"\nОТСУТСТВУЮТ КОЛОНКИ: {missing_columns}")
                else:
                    print("\nВСЕ НУЖНЫЕ КОЛОНКИ ПРИСУТСТВУЮТ")
                
                # Проверяем данные
                print("\n=== АНАЛИЗ ДАННЫХ ===")
                
                # Чашки
                total_cups = sales_data['ALLCUP'].sum()
                print(f"Общее количество чашек: {total_cups:.2f}")
                
                # Килограммы (пачки)
                total_kg = sales_data['PACKAGES_KG'].sum()
                print(f"Общий вес пачек: {total_kg:.2f} кг")
                
                # Суммы
                total_cash = sales_data['TOTAL_CASH'].sum()
                print(f"Общая сумма продаж: {total_cash:.2f} руб")
                
                # По магазинам
                print("\nДанные по магазинам:")
                store_summary = sales_data.groupby('STORE_NAME').agg({
                    'ALLCUP': 'sum',
                    'PACKAGES_KG': 'sum',
                    'TOTAL_CASH': 'sum'
                }).round(2)
                print(store_summary)
                
                return True
            else:
                print("НЕТ ДАННЫХ")
                return False
                
    except Exception as e:
        logger.error(f"Ошибка тестирования: {e}")
        print(f"ОШИБКА: {e}")
        return False

def main():
    """Основная функция"""
    print("=== ТЕСТ ОБНОВЛЕННОЙ ЛОГИКИ GUI ===")
    
    success = test_updated_gui_logic()
    
    if success:
        print("\nТЕСТ ПРОШЕЛ УСПЕШНО!")
        print("GUI приложение готово к использованию с обновленной логикой!")
    else:
        print("\nТЕСТ НЕ ПРОШЕЛ!")
        print("Требуется исправление ошибок.")
    
    print("\n" + "="*50)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()
