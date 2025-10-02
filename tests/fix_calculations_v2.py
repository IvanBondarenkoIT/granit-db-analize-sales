#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления расчетов сумм и килограммов - версия 2
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

def get_coffee_sales_with_weights(start_date, end_date):
    """Получает продажи кофе с правильным расчетом веса"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПОЛУЧЕНИЕ ПРОДАЖ КОФЕ С ВЕСОМ ({start_date} - {end_date}) ===")
            
            # SQL запрос для получения продаж кофе с информацией о товарах
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
                GD.SUMMA as ITEM_SUM,
                G.OWNER as PRODUCT_OWNER
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            coffee_data = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей продаж кофе: {len(coffee_data)}")
            
            if not coffee_data.empty:
                print("\nПервые 5 записей продаж кофе:")
                print(coffee_data.head())
                return coffee_data
            else:
                print("Нет данных продаж кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения продаж кофе: {e}")
        return None

def extract_weight_from_product_name(product_name):
    """Извлекает вес из названия товара"""
    import re
    
    if not product_name:
        return 0.25  # По умолчанию
    
    # Паттерны для поиска веса
    weight_patterns = [
        r'(\d+[,.]?\d*)\s*кг',
        r'(\d+[,.]?\d*)\s*kg',
        r'(\d+[,.]?\d*)\s*г',
        r'(\d+[,.]?\d*)\s*g',
        r'(\d+[,.]?\d*)\s*гр'
    ]
    
    for pattern in weight_patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            weight_str = match.group(1).replace(',', '.')
            try:
                weight = float(weight_str)
                # Если вес в граммах, переводим в кг
                if 'г' in product_name.lower() or 'g' in product_name.lower():
                    weight = weight / 1000
                return weight
            except ValueError:
                continue
    
    return 0.25  # По умолчанию

def calculate_correct_weights(coffee_data):
    """Рассчитывает правильные веса для продаж кофе"""
    if coffee_data is None or coffee_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ПРАВИЛЬНЫХ ВЕСОВ ===")
    
    # Добавляем колонку с весом товара
    coffee_data['ITEM_WEIGHT'] = coffee_data['PRODUCT_NAME'].apply(extract_weight_from_product_name)
    
    # Рассчитываем общий вес для каждой записи
    coffee_data['TOTAL_WEIGHT'] = coffee_data['QUANTITY'] * coffee_data['ITEM_WEIGHT']
    
    print("Примеры расчета веса:")
    sample = coffee_data.head(10)
    for idx, row in sample.iterrows():
        print(f"Товар: {row['PRODUCT_NAME']}")
        print(f"  Количество: {row['QUANTITY']}")
        print(f"  Вес за единицу: {row['ITEM_WEIGHT']} кг")
        print(f"  Общий вес: {row['TOTAL_WEIGHT']} кг")
        print()
    
    # Группируем по магазинам и датам
    grouped = coffee_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT': 'sum',
        'ITEM_SUM': 'sum'
    }).reset_index()
    
    print("Сгруппированные данные по весу:")
    print(grouped)
    
    return grouped

def compare_with_verification_data(cash_data, kg_data, our_cash, our_kg):
    """Сравнивает наши данные с эталонными"""
    print("\n=== СРАВНЕНИЕ С ДАННЫМИ СВЕРКИ ===")
    
    if our_cash is not None and not our_cash.empty:
        print("\nСРАВНЕНИЕ СУММ:")
        print("Наши данные:")
        print(our_cash)
        print("\nЭталонные данные:")
        print(cash_data)
    
    if our_kg is not None and not our_kg.empty:
        print("\nСРАВНЕНИЕ КИЛОГРАММОВ:")
        print("Наши данные:")
        print(our_kg)
        print("\nЭталонные данные:")
        print(kg_data)

def main():
    """Основная функция для тестирования и исправления расчетов"""
    print("=== ИСПРАВЛЕНИЕ РАСЧЕТОВ СУММ И КИЛОГРАММОВ - ВЕРСИЯ 2 ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Загружаем данные для сверки
    print("\n" + "="*50)
    print("ЭТАП 1: Загрузка данных для сверки")
    print("="*50)
    
    cash_verification, kg_verification = load_verification_data()
    if cash_verification is None or kg_verification is None:
        print("ОШИБКА: Не удалось загрузить данные для сверки")
        return
    
    # Этап 2: Получаем общую кассу
    print("\n" + "="*50)
    print("ЭТАП 2: Получение общей кассы")
    print("="*50)
    
    total_cash = get_total_cash_by_store_and_date("2025-09-29", "2025-09-30")
    
    # Этап 3: Получаем продажи кофе с весами
    print("\n" + "="*50)
    print("ЭТАП 3: Получение продаж кофе с весами")
    print("="*50)
    
    coffee_sales = get_coffee_sales_with_weights("2025-09-29", "2025-09-30")
    
    # Этап 4: Рассчитываем правильные веса
    print("\n" + "="*50)
    print("ЭТАП 4: Расчет правильных весов")
    print("="*50)
    
    correct_weights = calculate_correct_weights(coffee_sales)
    
    # Этап 5: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 5: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_data(cash_verification, kg_verification, total_cash, correct_weights)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)
    print("Следующие шаги:")
    print("1. Проанализировать различия в данных")
    print("2. Исправить расчеты в системе")
    print("3. Повторить тестирование")

if __name__ == "__main__":
    main()

