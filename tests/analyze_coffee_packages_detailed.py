#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Детальный анализ пачек кофе с разными весами
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

def analyze_coffee_packages_detailed(start_date, end_date):
    """Детальный анализ пачек кофе с разными весами"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ДЕТАЛЬНЫЙ АНАЛИЗ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            # Ищем пачки кофе
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
                D.SUMMA as TOTAL_SUM,
                G.OWNER as PRODUCT_OWNER,
                GG.NAME as GROUP_NAME,
                GG.ID as GROUP_ID
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND (
                    GG.NAME LIKE '%Coffee Blasecafe blend (250 g)%' OR
                    GG.NAME LIKE '%Coffee Blasercafe singl origin (250g)%' OR
                    GG.NAME LIKE '%Coffee Fresh%' OR
                    GG.NAME LIKE '%Coffee Blaser%'
                )
                AND NOT (
                    GG.NAME LIKE '%espresso%' OR
                    GG.NAME LIKE '%Cold%' OR
                    GG.NAME LIKE '%Tonic%' OR
                    GG.NAME LIKE '%Smoothie%' OR
                    GG.NAME LIKE '%Tropic%' OR
                    GG.NAME LIKE '%DRINKS%' OR
                    GG.NAME LIKE '%makers%' OR
                    GG.NAME LIKE '%Gaggia%' OR
                    GG.NAME LIKE '%Macap%' OR
                    GG.NAME LIKE '%Saeco%' OR
                    GG.NAME LIKE '%Handpresso%' OR
                    GG.NAME LIKE '%Melitta%' OR
                    GG.NAME LIKE '%Delonghi%' OR
                    GG.NAME LIKE '%accessories%' OR
                    GG.NAME LIKE '%Tech%' OR
                    GG.NAME LIKE '%Milk%' OR
                    GG.NAME LIKE '%Consumables%' OR
                    GG.NAME LIKE '%Cookies%' OR
                    GG.NAME LIKE '%SNO%' OR
                    GG.NAME LIKE '%Chocolate%' OR
                    GG.NAME LIKE '%TEA%' OR
                    GG.NAME LIKE '%Cleaning%'
                )
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей пачек кофе: {len(sales)}")
            
            if not sales.empty:
                print("\n=== ДЕТАЛЬНЫЙ АНАЛИЗ КАЖДОЙ ПАЧКИ ===")
                
                # Анализируем каждую пачку
                total_weight = 0
                for idx, row in sales.iterrows():
                    product_name = row['PRODUCT_NAME']
                    quantity = row['QUANTITY']
                    
                    # Извлекаем вес из названия
                    weight = extract_weight_from_package_name(product_name)
                    total_weight_item = quantity * weight
                    total_weight += total_weight_item
                    
                    print(f"\n{product_name}")
                    print(f"  Количество: {quantity}")
                    print(f"  Вес за единицу: {weight} кг")
                    print(f"  Общий вес: {total_weight_item} кг")
                    print(f"  Группа: {row['GROUP_NAME']}")
                    print(f"  Магазин: {row['STORE_NAME']}")
                    print(f"  Дата: {row['SALE_DATE']}")
                
                print(f"\n=== ИТОГО ===")
                print(f"Общий вес всех пачек: {total_weight:.4f} кг")
                
                # Группируем по магазинам и датам
                grouped = sales.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum'
                }).reset_index()
                
                print(f"\n=== ГРУППИРОВКА ПО МАГАЗИНАМ И ДАТАМ ===")
                for idx, row in grouped.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE']
                    quantity = row['QUANTITY']
                    
                    # Получаем товары для этого магазина и даты
                    store_sales = sales[(sales['STORE_NAME'] == store) & (sales['SALE_DATE'] == date)]
                    
                    print(f"\n{store} - {date}")
                    print(f"  Общее количество пачек: {quantity}")
                    
                    store_weight = 0
                    for _, item in store_sales.iterrows():
                        weight = extract_weight_from_package_name(item['PRODUCT_NAME'])
                        item_weight = item['QUANTITY'] * weight
                        store_weight += item_weight
                        print(f"    {item['PRODUCT_NAME']}: {item['QUANTITY']} × {weight} = {item_weight:.4f} кг")
                    
                    print(f"  ИТОГО для {store} {date}: {store_weight:.4f} кг")
                
                return sales
            else:
                print("Нет пачек кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа пачек кофе: {e}")
        return None

def extract_weight_from_package_name(product_name):
    """Извлекает вес из названия пачки кофе"""
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

def main():
    """Основная функция"""
    print("=== ДЕТАЛЬНЫЙ АНАЛИЗ ПАЧЕК КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Анализируем пачки кофе
    print("\n" + "="*50)
    print("АНАЛИЗ ПАЧЕК КОФЕ")
    print("="*50)
    
    sales_data = analyze_coffee_packages_detailed("2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

