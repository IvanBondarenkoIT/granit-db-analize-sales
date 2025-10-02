#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Упрощенный анализ ограничений оригинального запроса
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

def analyze_constraints_simple():
    """Упрощенный анализ ограничений"""
    try:
        with DatabaseConnector() as db:
            print("=== АНАЛИЗ ОГРАНИЧЕНИЙ ОРИГИНАЛЬНОГО ЗАПРОСА ===")
            
            # 1. Анализируем STORGRPID (группы магазинов)
            print("\n1. АНАЛИЗ STORGRPID (группы магазинов):")
            query1 = """
            SELECT ID, NAME 
            FROM storgrp 
            WHERE ID IN ('27','43','44','46')
            ORDER BY ID
            """
            stores = db.execute_query(query1)
            print("Группы магазинов:")
            for idx, row in stores.iterrows():
                print(f"  ID: {row['ID']}, Название: {row['NAME']}")
            
            # 2. Анализируем CSDTKTHBID (типы касс)
            print("\n2. АНАЛИЗ CSDTKTHBID (типы касс):")
            query2 = """
            SELECT ID, NAME 
            FROM csdtkthb 
            WHERE ID IN ('1', '2', '3','5')
            ORDER BY ID
            """
            cash_types = db.execute_query(query2)
            print("Типы касс:")
            for idx, row in cash_types.iterrows():
                print(f"  ID: {row['ID']}, Название: {row['NAME']}")
            
            # 3. Анализируем товары кофе с учетом ограничений
            print("\n3. АНАЛИЗ ТОВАРОВ КОФЕ С ОГРАНИЧЕНИЯМИ:")
            query3 = """
            SELECT DISTINCT
                G.ID,
                G.NAME,
                G.OWNER,
                GG.NAME as GROUP_NAME,
                GG.ID as GROUP_ID
            FROM Goods G
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            ORDER BY G.NAME
            """
            coffee_products = db.execute_query(query3)
            print(f"Найдено товаров кофе: {len(coffee_products)}")
            
            # Группируем по группам товаров
            if not coffee_products.empty:
                group_counts = coffee_products.groupby(['GROUP_NAME', 'GROUP_ID']).size().reset_index(name='COUNT')
                print("\nГруппы товаров кофе:")
                for idx, row in group_counts.iterrows():
                    print(f"  Группа: {row['GROUP_NAME']} (ID: {row['GROUP_ID']}) - {row['COUNT']} товаров")
            
            # 4. Анализируем продажи с учетом всех ограничений
            print("\n4. АНАЛИЗ ПРОДАЖ С ОГРАНИЧЕНИЯМИ:")
            query4 = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
                G.OWNER as PRODUCT_OWNER,
                GG.NAME as GROUP_NAME,
                D.STORGRPID,
                D.CSDTKTHBID
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query4, ("2025-09-29", "2025-09-30"))
            print(f"Продажи с ограничениями: {len(sales)} записей")
            
            if not sales.empty:
                # Анализируем по группам товаров
                group_sales = sales.groupby(['GROUP_NAME', 'STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum'
                }).reset_index()
                
                print("\nПродажи по группам товаров:")
                for group in group_sales['GROUP_NAME'].unique():
                    group_data = group_sales[group_sales['GROUP_NAME'] == group]
                    total_qty = group_data['QUANTITY'].sum()
                    print(f"\n  Группа: {group}")
                    print(f"  Общее количество: {total_qty}")
                    
                    # Показываем по магазинам
                    for store in group_data['STORE_NAME'].unique():
                        store_data = group_data[group_data['STORE_NAME'] == store]
                        store_total = store_data['QUANTITY'].sum()
                        print(f"    {store}: {store_total}")
                
                # Анализируем товары с весом в названии
                print("\n5. АНАЛИЗ ТОВАРОВ С ВЕСОМ В НАЗВАНИИ:")
                weight_products = sales[sales['PRODUCT_NAME'].str.contains(r'\d+[.,]?\d*\s*(кг|kg|г|g|гр)', case=False, na=False)]
                
                if not weight_products.empty:
                    print(f"Товары с весом в названии: {len(weight_products)} записей")
                    
                    # Группируем по товарам
                    product_sales = weight_products.groupby(['PRODUCT_NAME', 'STORE_NAME', 'SALE_DATE']).agg({
                        'QUANTITY': 'sum'
                    }).reset_index()
                    
                    print("\nПродажи товаров с весом:")
                    for idx, row in product_sales.iterrows():
                        print(f"  {row['PRODUCT_NAME']} - {row['STORE_NAME']} ({row['SALE_DATE'].strftime('%Y-%m-%d')}): {row['QUANTITY']}")
                else:
                    print("Товары с весом в названии не найдены")
                
                return sales, group_sales
            else:
                print("Нет продаж с ограничениями")
                return None, None
                
    except Exception as e:
        logger.error(f"Ошибка анализа ограничений: {e}")
        return None, None

def extract_weight_from_name(product_name):
    """Извлекает вес из названия товара"""
    import re
    
    if not product_name:
        return 0
    
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
    
    return 0

def calculate_weights_with_constraints(sales_data):
    """Рассчитывает веса с учетом ограничений"""
    if sales_data is None or sales_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСОВ С ОГРАНИЧЕНИЯМИ ===")
    
    # Добавляем расчет веса
    sales_data['ITEM_WEIGHT'] = sales_data['PRODUCT_NAME'].apply(extract_weight_from_name)
    sales_data['TOTAL_WEIGHT'] = sales_data['QUANTITY'] * sales_data['ITEM_WEIGHT']
    
    # Группируем по магазинам и датам
    grouped = sales_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT': 'sum'
    }).reset_index()
    
    print("Итоговые килограммы по магазинам:")
    print(grouped)
    
    return grouped

def compare_with_verification(constrained_data):
    """Сравнивает с эталонными данными"""
    try:
        import pandas as pd
        
        print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
        
        # Загружаем эталонные данные
        excel_file = "data/данные для сверки.xlsx"
        kg_verification = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        
        print("Эталонные данные по килограммам:")
        print(kg_verification)
        
        if constrained_data is not None and not constrained_data.empty:
            print("\nНаши данные с ограничениями:")
            print(constrained_data)
            
            print("\nСравнительная таблица:")
            print("Магазин | Дата | Наши данные | Эталон | Разница | Статус")
            print("-" * 70)
            
            for idx, row in constrained_data.iterrows():
                store = row['STORE_NAME']
                date = row['SALE_DATE'].strftime('%Y-%m-%d')
                our_weight = row['TOTAL_WEIGHT']
                
                # Ищем эталонные данные
                store_row = kg_verification[kg_verification['Unnamed: 0'] == store]
                if not store_row.empty:
                    if date == '2025-09-29':
                        ref_weight = store_row.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_weight = store_row.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_weight = 0
                    
                    diff = our_weight - ref_weight
                    if abs(diff) < 0.1:
                        status = "OK"
                    elif abs(diff) < 0.5:
                        status = "ХОРОШО"
                    else:
                        status = "ПЛОХО"
                    
                    print(f"{store} | {date} | {our_weight:.2f} | {ref_weight:.2f} | {diff:+.2f} | {status}")
                else:
                    print(f"{store} | {date} | {our_weight:.2f} | НЕТ ДАННЫХ | - | -")
        
    except Exception as e:
        logger.error(f"Ошибка сравнения с эталонными данными: {e}")

def main():
    """Основная функция"""
    print("=== АНАЛИЗ ОГРАНИЧЕНИЙ ОРИГИНАЛЬНОГО ЗАПРОСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Анализируем ограничения
    print("\n" + "="*50)
    print("ЭТАП 1: Анализ ограничений запроса")
    print("="*50)
    
    sales_data, group_data = analyze_constraints_simple()
    
    # Этап 2: Рассчитываем веса с ограничениями
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов с ограничениями")
    print("="*50)
    
    weights_data = calculate_weights_with_constraints(sales_data)
    
    # Этап 3: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification(weights_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

