#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления расчетов сумм и килограммов
Анализирует данные сверки и тестирует исправления
"""

import pandas as pd
import sys
import os
from datetime import datetime, date

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_connector import DatabaseConnector
from logger_config import setup_logger

# Настраиваем логирование
logger = setup_logger(__name__)

def load_verification_data():
    """Загружает данные для сверки из Excel файла"""
    try:
        # Загружаем данные сверки
        excel_file = "data/данные для сверки.xlsx"
        
        # Читаем вкладку "Общая касса"
        cash_data = pd.read_excel(excel_file, sheet_name="Общая касса")
        logger.info(f"Загружены данные общей кассы: {len(cash_data)} строк")
        print("=== ДАННЫЕ ОБЩЕЙ КАССЫ ===")
        print(cash_data)
        
        # Читаем вкладку "Количество килограмм"
        kg_data = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        logger.info(f"Загружены данные по килограммам: {len(kg_data)} строк")
        print("\n=== ДАННЫЕ ПО КИЛОГРАММАМ ===")
        print(kg_data)
        
        return cash_data, kg_data
        
    except Exception as e:
        logger.error(f"Ошибка загрузки данных сверки: {e}")
        return None, None

def test_current_calculations():
    """Тестирует текущие расчеты из нашей системы"""
    try:
        with DatabaseConnector() as db:
            # Тестируем за период 29-30 сентября 2025
            start_date = "2025-09-29"
            end_date = "2025-09-30"
            
            print(f"\n=== ТЕСТ ТЕКУЩИХ РАСЧЕТОВ ({start_date} - {end_date}) ===")
            
            # Получаем данные по кофе
            coffee_data = db.get_coffee_sales_by_type(start_date, end_date)
            print(f"Получено записей по кофе: {len(coffee_data)}")
            
            if not coffee_data.empty:
                print("\nПервые 5 записей:")
                print(coffee_data.head())
                
                # Группируем по магазинам и датам
                grouped = coffee_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                print(f"\nСгруппированные данные ({len(grouped)} записей):")
                print(grouped)
                
                return coffee_data, grouped
            else:
                print("Нет данных по кофе за указанный период")
                return None, None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования текущих расчетов: {e}")
        return None, None

def analyze_product_weights():
    """Анализирует информацию о весе товаров в базе данных"""
    try:
        with DatabaseConnector() as db:
            print("\n=== АНАЛИЗ ВЕСА ТОВАРОВ ===")
            
            # Получаем все товары кофе
            coffee_products = db.get_coffee_products()
            print(f"Найдено товаров кофе: {len(coffee_products)}")
            
            if not coffee_products.empty:
                # Анализируем названия товаров на предмет веса
                print("\nАнализ названий товаров на предмет веса:")
                for idx, row in coffee_products.head(10).iterrows():
                    name = row['NAME']
                    print(f"ID: {row['ID']}, Название: {name}")
                    
                    # Ищем вес в названии
                    import re
                    weight_patterns = [
                        r'(\d+[,.]?\d*)\s*кг',
                        r'(\d+[,.]?\d*)\s*kg',
                        r'(\d+[,.]?\d*)\s*г',
                        r'(\d+[,.]?\d*)\s*g',
                        r'(\d+[,.]?\d*)\s*гр'
                    ]
                    
                    found_weight = None
                    for pattern in weight_patterns:
                        match = re.search(pattern, name, re.IGNORECASE)
                        if match:
                            weight_str = match.group(1).replace(',', '.')
                            try:
                                weight = float(weight_str)
                                if 'г' in name.lower() or 'g' in name.lower():
                                    weight = weight / 1000  # переводим граммы в кг
                                found_weight = weight
                                break
                            except ValueError:
                                continue
                    
                    if found_weight:
                        print(f"  -> Найден вес: {found_weight} кг")
                    else:
                        print(f"  -> Вес не найден, используем 0.25 кг")
                
                return coffee_products
            else:
                print("Товары кофе не найдены")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа веса товаров: {e}")
        return None

def get_total_cash_by_store_and_date(start_date, end_date):
    """Получает общую кассу по магазинам и датам (без фильтрации по товарам)"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПОЛУЧЕНИЕ ОБЩЕЙ КАССЫ ({start_date} - {end_date}) ===")
            
            # SQL запрос для получения общей кассы по магазинам и датам
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(D.SUMMA) as TOTAL_CASH
            FROM storzakazdt D 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
            GROUP BY stgp.name, D.DAT_
            ORDER BY stgp.name, D.DAT_
            """
            
            cash_data = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей общей кассы: {len(cash_data)}")
            
            if not cash_data.empty:
                print("\nДанные общей кассы:")
                print(cash_data)
                return cash_data
            else:
                print("Нет данных общей кассы за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения общей кассы: {e}")
        return None

def main():
    """Основная функция для тестирования и исправления расчетов"""
    print("=== ИСПРАВЛЕНИЕ РАСЧЕТОВ СУММ И КИЛОГРАММОВ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Загружаем данные для сверки
    print("\n" + "="*50)
    print("ЭТАП 1: Загрузка данных для сверки")
    print("="*50)
    
    cash_verification, kg_verification = load_verification_data()
    if cash_verification is None or kg_verification is None:
        print("ОШИБКА: Не удалось загрузить данные для сверки")
        return
    
    # Этап 2: Тестируем текущие расчеты
    print("\n" + "="*50)
    print("ЭТАП 2: Тестирование текущих расчетов")
    print("="*50)
    
    coffee_data, grouped_data = test_current_calculations()
    
    # Этап 3: Анализируем вес товаров
    print("\n" + "="*50)
    print("ЭТАП 3: Анализ веса товаров")
    print("="*50)
    
    products = analyze_product_weights()
    
    # Этап 4: Получаем общую кассу
    print("\n" + "="*50)
    print("ЭТАП 4: Получение общей кассы")
    print("="*50)
    
    total_cash = get_total_cash_by_store_and_date("2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)
    print("Следующие шаги:")
    print("1. Сравнить данные общей кассы с данными сверки")
    print("2. Исправить расчет сумм в системе")
    print("3. Проанализировать расчет килограммов")
    print("4. Внести исправления в код")

if __name__ == "__main__":
    main()
