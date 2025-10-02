#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ расхождения в килограммах
Исследуем почему наши данные в 3-5 раз больше эталонных
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

def analyze_products_by_owner():
    """Анализирует товары по группам (OWNER)"""
    try:
        with DatabaseConnector() as db:
            print("=== АНАЛИЗ ТОВАРОВ ПО ГРУППАМ (OWNER) ===")
            
            # Получаем все товары кофе с группировкой по OWNER
            query = """
            SELECT 
                G.OWNER as PRODUCT_OWNER,
                COUNT(*) as PRODUCT_COUNT,
                STRING_AGG(DISTINCT G.NAME, '; ') as SAMPLE_NAMES
            FROM Goods G
            WHERE G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            GROUP BY G.OWNER
            ORDER BY G.OWNER
            """
            
            products = db.execute_query(query)
            print(f"Найдено групп товаров: {len(products)}")
            
            if not products.empty:
                print("\nГруппы товаров кофе:")
                for idx, row in products.iterrows():
                    owner = row['PRODUCT_OWNER']
                    count = row['PRODUCT_COUNT']
                    names = row['SAMPLE_NAMES'][:100] + "..." if len(row['SAMPLE_NAMES']) > 100 else row['SAMPLE_NAMES']
                    
                    print(f"\nOWNER {owner}: {count} товаров")
                    print(f"  Примеры: {names}")
                
                return products
            else:
                print("Товары кофе не найдены")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа товаров по группам: {e}")
        return None

def analyze_sales_by_owner(start_date, end_date):
    """Анализирует продажи по группам товаров"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== АНАЛИЗ ПРОДАЖ ПО ГРУППАМ ({start_date} - {end_date}) ===")
            
            query = """
            SELECT 
                G.OWNER as PRODUCT_OWNER,
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(GD.SOURCE) as TOTAL_QUANTITY,
                COUNT(*) as TRANSACTION_COUNT
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
            GROUP BY G.OWNER, stgp.name, D.DAT_
            ORDER BY G.OWNER, stgp.name, D.DAT_
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей продаж: {len(sales)}")
            
            if not sales.empty:
                print("\nПродажи по группам:")
                print(sales)
                
                # Группируем по OWNER для анализа
                by_owner = sales.groupby('PRODUCT_OWNER').agg({
                    'TOTAL_QUANTITY': 'sum',
                    'TRANSACTION_COUNT': 'sum'
                }).reset_index()
                
                print("\nСуммарные продажи по группам:")
                print(by_owner)
                
                return sales, by_owner
            else:
                print("Нет данных продаж за указанный период")
                return None, None
                
    except Exception as e:
        logger.error(f"Ошибка анализа продаж по группам: {e}")
        return None, None

def analyze_specific_products():
    """Анализирует конкретные товары, которые могут быть в эталонных данных"""
    try:
        with DatabaseConnector() as db:
            print("\n=== АНАЛИЗ КОНКРЕТНЫХ ТОВАРОВ ===")
            
            # Ищем товары с весом в названии
            query = """
            SELECT 
                G.ID,
                G.NAME,
                G.OWNER,
                COUNT(*) as SALES_COUNT,
                SUM(GD.SOURCE) as TOTAL_QUANTITY
            FROM Goods G
            JOIN STORZDTGDS GD ON G.ID = GD.GODSID
            JOIN storzakazdt D ON GD.SZID = D.ID
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
                AND (G.NAME LIKE '%кг%' OR G.NAME LIKE '%kg%' OR G.NAME LIKE '%г%' OR G.NAME LIKE '%g%')
            GROUP BY G.ID, G.NAME, G.OWNER
            ORDER BY TOTAL_QUANTITY DESC
            """
            
            products = db.execute_query(query, ("2025-09-29", "2025-09-30"))
            print(f"Найдено товаров с весом в названии: {len(products)}")
            
            if not products.empty:
                print("\nТовары с весом в названии:")
                for idx, row in products.iterrows():
                    print(f"ID: {row['ID']}, Название: {row['NAME']}")
                    print(f"  OWNER: {row['OWNER']}, Продаж: {row['SALES_COUNT']}, Количество: {row['TOTAL_QUANTITY']}")
                    print()
                
                return products
            else:
                print("Товары с весом в названии не найдены")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа конкретных товаров: {e}")
        return None

def test_different_weight_calculations():
    """Тестирует разные способы расчета веса"""
    try:
        with DatabaseConnector() as db:
            print("\n=== ТЕСТИРОВАНИЕ РАЗНЫХ СПОСОБОВ РАСЧЕТА ВЕСА ===")
            
            # Получаем данные для тестирования
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
            
            data = db.execute_query(query, ("2025-09-29", "2025-09-30"))
            
            if data.empty:
                print("Нет данных для тестирования")
                return
            
            # Тестируем разные способы расчета веса
            print("\nТестирование разных способов расчета веса:")
            
            # Способ 1: Только товары с весом в названии
            weight_products = data[data['PRODUCT_NAME'].str.contains(r'\d+[,.]?\d*\s*(кг|kg|г|g)', case=False, na=False)]
            weight_1 = weight_products.groupby(['STORE_NAME', 'SALE_DATE'])['QUANTITY'].sum() * 0.25  # предполагаем 0.25 кг за единицу
            
            print("\nСпособ 1 - Только товары с весом в названии:")
            print(weight_1)
            
            # Способ 2: Только определенные OWNER (например, только CaotinaCup)
            caotina_products = data[data['PRODUCT_OWNER'].isin(['24491','21385'])]
            weight_2 = caotina_products.groupby(['STORE_NAME', 'SALE_DATE'])['QUANTITY'].sum() * 0.25
            
            print("\nСпособ 2 - Только CaotinaCup (OWNER 24491, 21385):")
            print(weight_2)
            
            # Способ 3: Только определенные товары (например, с "portion" в названии)
            portion_products = data[data['PRODUCT_NAME'].str.contains('portion', case=False, na=False)]
            weight_3 = portion_products.groupby(['STORE_NAME', 'SALE_DATE'])['QUANTITY'].sum() * 0.25
            
            print("\nСпособ 3 - Только товары с 'portion' в названии:")
            print(weight_3)
            
    except Exception as e:
        logger.error(f"Ошибка тестирования способов расчета веса: {e}")

def main():
    """Основная функция"""
    print("=== АНАЛИЗ РАСХОЖДЕНИЯ В КИЛОГРАММАХ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Анализируем товары по группам
    print("\n" + "="*50)
    print("ЭТАП 1: Анализ товаров по группам")
    print("="*50)
    
    products = analyze_products_by_owner()
    
    # Этап 2: Анализируем продажи по группам
    print("\n" + "="*50)
    print("ЭТАП 2: Анализ продаж по группам")
    print("="*50)
    
    sales, by_owner = analyze_sales_by_owner("2025-09-29", "2025-09-30")
    
    # Этап 3: Анализируем конкретные товары
    print("\n" + "="*50)
    print("ЭТАП 3: Анализ конкретных товаров")
    print("="*50)
    
    specific_products = analyze_specific_products()
    
    # Этап 4: Тестируем разные способы расчета
    print("\n" + "="*50)
    print("ЭТАП 4: Тестирование разных способов расчета веса")
    print("="*50)
    
    test_different_weight_calculations()
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

