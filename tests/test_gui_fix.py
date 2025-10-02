#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТ ИСПРАВЛЕНИЯ GUI - ПРОВЕРКА КОЛОНОК
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

def test_gui_columns_fix():
    """Тестирует исправление колонок в GUI"""
    print("=== ТЕСТ ИСПРАВЛЕНИЯ КОЛОНОК GUI ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        with DatabaseConnector() as db:
            # Тестируем новый метод
            print("\n1. Тестирование метода get_coffee_sales_with_packages...")
            sales_data = db.get_coffee_sales_with_packages(
                store_ids=[27, 43, 44, 46],  # Основные магазины
                start_date="2025-09-29",
                end_date="2025-09-30"
            )
            
            print(f"   Получено записей: {len(sales_data)}")
            
            if not sales_data.empty:
                print("\n2. Проверка структуры данных:")
                print(f"   Колонки: {list(sales_data.columns)}")
                
                # Проверяем наличие нужных колонок
                required_columns = ['STORE_NAME', 'ORDER_DATE', 'ALLCUP', 'PACKAGES_KG', 'TOTAL_CASH']
                missing_columns = [col for col in required_columns if col not in sales_data.columns]
                
                if missing_columns:
                    print(f"   ОШИБКА: Отсутствуют колонки: {missing_columns}")
                    return False
                else:
                    print("   УСПЕХ: Все нужные колонки присутствуют")
                
                # Тестируем группировку (как в GUI)
                print("\n3. Тестирование группировки данных...")
                sales_data['TIME_PERIOD'] = sales_data['ORDER_DATE'].dt.date
                
                grouped = sales_data.groupby(['STORE_NAME', 'TIME_PERIOD']).agg({
                    'ALLCUP': 'sum',
                    'PACKAGES_KG': 'sum',
                    'TOTAL_CASH': 'sum',
                }).reset_index()
                
                print(f"   Группировка выполнена: {len(grouped)} групп")
                
                # Тестируем сводную таблицу
                print("\n4. Тестирование сводной таблицы...")
                pivot_table = grouped.pivot_table(
                    index='STORE_NAME',
                    columns='TIME_PERIOD',
                    values=['ALLCUP', 'PACKAGES_KG', 'TOTAL_CASH'],
                    fill_value=0
                )
                
                print(f"   Сводная таблица создана: {len(pivot_table)} магазинов")
                
                # Тестируем доступ к данным
                print("\n5. Тестирование доступа к данным...")
                time_periods = sorted(grouped['TIME_PERIOD'].unique())
                
                for store in pivot_table.index:
                    for period in time_periods:
                        if period in pivot_table.columns.get_level_values(1):
                            cups = pivot_table.loc[store, ('ALLCUP', period)]
                            kg = pivot_table.loc[store, ('PACKAGES_KG', period)]
                            total = pivot_table.loc[store, ('TOTAL_CASH', period)]
                            
                            # Формируем ячейку как в GUI
                            cell_content = f"Чашки: {cups:.0f} шт\nКг: {kg:.2f} кг\nСумма: {total:.2f} лари"
                            print(f"   {store} {period}: {cell_content}")
                            break  # Показываем только первый период для краткости
                    break  # Показываем только первый магазин для краткости
                
                print("\nУСПЕХ: Все тесты прошли успешно!")
                return True
            else:
                print("ОШИБКА: Нет данных")
                return False
                
    except Exception as e:
        print(f"ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("=== ТЕСТ ИСПРАВЛЕНИЯ GUI ===")
    
    success = test_gui_columns_fix()
    
    if success:
        print("\nВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("GUI приложение исправлено и готово к использованию!")
    else:
        print("\nТЕСТЫ НЕ ПРОШЛИ!")
        print("Требуется дополнительное исправление.")
    
    print("\n" + "="*50)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()
