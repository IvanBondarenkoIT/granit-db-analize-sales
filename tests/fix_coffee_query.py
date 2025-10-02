#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для исправления запроса продаж кофе
Используем правильные поля из таблицы STORZDTGDS
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

def get_coffee_sales_corrected(start_date, end_date):
    """Получает продажи кофе с исправленным запросом"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ПОЛУЧЕНИЕ ПРОДАЖ КОФЕ ({start_date} - {end_date}) ===")
            
            # Исправленный запрос - используем только поля, которые точно существуют
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
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
                print("\nПервые 5 записей:")
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

def calculate_weights_and_group(coffee_data):
    """Рассчитывает веса и группирует данные"""
    if coffee_data is None or coffee_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСОВ И ГРУППИРОВКА ===")
    
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
        'TOTAL_WEIGHT': 'sum'
    }).reset_index()
    
    print("Сгруппированные данные по весу:")
    print(grouped)
    
    return grouped

def load_verification_data():
    """Загружает данные для сверки"""
    try:
        import pandas as pd
        excel_file = "data/данные для сверки.xlsx"
        kg_data = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        print("\n=== ЭТАЛОННЫЕ ДАННЫЕ ПО КИЛОГРАММАМ ===")
        print(kg_data)
        return kg_data
    except Exception as e:
        logger.error(f"Ошибка загрузки данных сверки: {e}")
        return None

def compare_weights(our_data, verification_data):
    """Сравнивает наши данные с эталонными"""
    print("\n=== СРАВНЕНИЕ КИЛОГРАММОВ ===")
    
    if our_data is None or our_data.empty:
        print("Нет наших данных для сравнения")
        return
    
    print("Наши данные:")
    print(our_data)
    
    if verification_data is not None:
        print("\nЭталонные данные:")
        print(verification_data)
        
        # Создаем сводную таблицу для сравнения
        print("\nСравнительная таблица:")
        for idx, row in our_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            our_weight = row['TOTAL_WEIGHT']
            
            print(f"{store} ({date}): {our_weight:.2f} кг")

def main():
    """Основная функция"""
    print("=== ИСПРАВЛЕНИЕ ЗАПРОСА ПРОДАЖ КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Получаем продажи кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Получение продаж кофе")
    print("="*50)
    
    coffee_data = get_coffee_sales_corrected("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов")
    print("="*50)
    
    weights_data = calculate_weights_and_group(coffee_data)
    
    # Этап 3: Загружаем эталонные данные
    print("\n" + "="*50)
    print("ЭТАП 3: Загрузка эталонных данных")
    print("="*50)
    
    verification_data = load_verification_data()
    
    # Этап 4: Сравниваем данные
    print("\n" + "="*50)
    print("ЭТАП 4: Сравнение данных")
    print("="*50)
    
    compare_weights(weights_data, verification_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

