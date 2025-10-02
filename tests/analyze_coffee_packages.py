#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ пачек кофе (не напитков) для правильного расчета килограммов
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

def analyze_coffee_packages(start_date, end_date):
    """Анализирует пачки кофе (не напитки)"""
    try:
        with DatabaseConnector() as db:
            print(f"=== АНАЛИЗ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            # Сначала посмотрим на все товары кофе и их названия
            query = """
            SELECT DISTINCT
                G.ID,
                G.NAME,
                G.OWNER,
                GG.NAME as GROUP_NAME
            FROM Goods G
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            ORDER BY G.NAME
            """
            
            products = db.execute_query(query)
            print(f"Найдено товаров кофе: {len(products)}")
            
            if not products.empty:
                print("\nВсе товары кофе:")
                for idx, row in products.iterrows():
                    print(f"ID: {row['ID']}, Название: {row['NAME']}")
                    print(f"  OWNER: {row['OWNER']}, Группа: {row['GROUP_NAME']}")
                    print()
                
                # Ищем товары, которые могут быть пачками (не напитками)
                print("=== ПОИСК ПАЧЕК КОФЕ ===")
                package_keywords = ['пачка', 'пак', 'упак', 'кг', 'kg', 'г', 'g', 'молотый', 'зерно', 'beans', 'ground']
                
                packages = []
                drinks = []
                
                for idx, row in products.iterrows():
                    name = row['NAME'].lower()
                    is_package = any(keyword in name for keyword in package_keywords)
                    
                    if is_package:
                        packages.append(row)
                    else:
                        drinks.append(row)
                
                print(f"Найдено пачек кофе: {len(packages)}")
                print(f"Найдено напитков: {len(drinks)}")
                
                print("\nПАЧКИ КОФЕ:")
                for pkg in packages:
                    print(f"  {pkg['NAME']} (OWNER: {pkg['OWNER']})")
                
                print("\nНАПИТКИ:")
                for drink in drinks:
                    print(f"  {drink['NAME']} (OWNER: {drink['OWNER']})")
                
                return packages, drinks
            else:
                print("Товары кофе не найдены")
                return None, None
                
    except Exception as e:
        logger.error(f"Ошибка анализа пачек кофе: {e}")
        return None, None

def get_coffee_packages_sales(start_date, end_date, package_ids):
    """Получает продажи пачек кофе"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПРОДАЖИ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            if not package_ids:
                print("Нет пачек кофе для анализа")
                return None
            
            # Создаем список ID пачек
            ids_str = ','.join([str(pkg['ID']) for pkg in package_ids])
            
            query = f"""
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
                AND G.ID IN ({ids_str})
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей продаж пачек: {len(sales)}")
            
            if not sales.empty:
                print("\nПродажи пачек кофе:")
                print(sales)
                
                # Группируем по магазинам и датам
                grouped = sales.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum'
                }).reset_index()
                
                print("\nСгруппированные продажи пачек:")
                print(grouped)
                
                return sales, grouped
            else:
                print("Нет продаж пачек кофе за указанный период")
                return None, None
                
    except Exception as e:
        logger.error(f"Ошибка получения продаж пачек: {e}")
        return None, None

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

def calculate_package_weights(sales_data):
    """Рассчитывает веса пачек кофе"""
    if sales_data is None or sales_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСОВ ПАЧЕК КОФЕ ===")
    
    # Добавляем расчет веса
    sales_data['ITEM_WEIGHT'] = sales_data['PRODUCT_NAME'].apply(extract_weight_from_package_name)
    sales_data['TOTAL_WEIGHT'] = sales_data['QUANTITY'] * sales_data['ITEM_WEIGHT']
    
    print("Расчет веса по пачкам:")
    for idx, row in sales_data.iterrows():
        print(f"  {row['PRODUCT_NAME']}")
        print(f"    Количество: {row['QUANTITY']}")
        print(f"    Вес за единицу: {row['ITEM_WEIGHT']} кг")
        print(f"    Общий вес: {row['TOTAL_WEIGHT']} кг")
        print()
    
    # Группируем по магазинам и датам
    grouped = sales_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT': 'sum'
    }).reset_index()
    
    print("Итоговые килограммы пачек по магазинам:")
    print(grouped)
    
    return grouped

def compare_with_verification(packages_data):
    """Сравнивает с эталонными данными"""
    try:
        import pandas as pd
        
        print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
        
        # Загружаем эталонные данные
        excel_file = "data/данные для сверки.xlsx"
        kg_verification = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        
        print("Эталонные данные по килограммам:")
        print(kg_verification)
        
        if packages_data is not None and not packages_data.empty:
            print("\nНаши данные по пачкам кофе:")
            print(packages_data)
            
            print("\nСравнительная таблица:")
            print("Магазин | Дата | Наши пачки | Эталон кг | Разница")
            print("-" * 50)
            
            for idx, row in packages_data.iterrows():
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
                    status = "OK" if abs(diff) < 0.1 else "РАЗНИЦА"
                    
                    print(f"{store} | {date} | {our_weight:.2f} | {ref_weight:.2f} | {diff:+.2f} {status}")
                else:
                    print(f"{store} | {date} | {our_weight:.2f} | НЕТ ДАННЫХ | -")
        
    except Exception as e:
        logger.error(f"Ошибка сравнения с эталонными данными: {e}")

def main():
    """Основная функция"""
    print("=== АНАЛИЗ ПАЧЕК КОФЕ (НЕ НАПИТКОВ) ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Анализируем товары кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Анализ товаров кофе")
    print("="*50)
    
    packages, drinks = analyze_coffee_packages("2025-09-29", "2025-09-30")
    
    # Этап 2: Получаем продажи пачек
    print("\n" + "="*50)
    print("ЭТАП 2: Продажи пачек кофе")
    print("="*50)
    
    sales_data, grouped_data = get_coffee_packages_sales("2025-09-29", "2025-09-30", packages)
    
    # Этап 3: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 3: Расчет весов пачек")
    print("="*50)
    
    weights_data = calculate_package_weights(sales_data)
    
    # Этап 4: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 4: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification(weights_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

