#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА МАГАЗИНА BATUMIMALL
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

def check_batumimall_store():
    """Проверяет, есть ли магазин BatumiMall в базе данных"""
    try:
        with DatabaseConnector() as db:
            print("=== ПРОВЕРКА МАГАЗИНА BATUMIMALL ===")
            
            # Ищем все магазины
            query = """
            SELECT DISTINCT 
                ID,
                NAME
            FROM storgrp
            ORDER BY NAME
            """
            
            stores = db.execute_query(query)
            print(f"Найдено магазинов: {len(stores)}")
            
            if not stores.empty:
                print("\nВсе магазины в базе данных:")
                for idx, row in stores.iterrows():
                    store_id = row['ID']
                    store_name = row['NAME']
                    print(f"  ID: {store_id} | {store_name}")
                
                # Ищем магазины с "Batumi" в названии
                batumi_stores = stores[stores['NAME'].str.contains('Batumi', case=False, na=False)]
                print(f"\nМагазины с 'Batumi' в названии: {len(batumi_stores)}")
                for idx, row in batumi_stores.iterrows():
                    store_id = row['ID']
                    store_name = row['NAME']
                    print(f"  ID: {store_id} | {store_name}")
                
                return stores
            else:
                print("Нет магазинов в базе данных")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка проверки магазинов: {e}")
        return None

def check_sales_for_batumimall(start_date, end_date):
    """Проверяет продажи для магазинов с Batumi"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПРОДАЖИ ДЛЯ МАГАЗИНОВ С BATUMI ({start_date} - {end_date}) ===")
            
            # Ищем продажи для магазинов с Batumi
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
                D.SUMMA as TOTAL_SUM,
                G.OWNER as PRODUCT_OWNER,
                GG.NAME as GROUP_NAME
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND stgp.name LIKE '%Batumi%'
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Найдено продаж для магазинов с Batumi: {len(sales)}")
            
            if not sales.empty:
                print("\nПродажи для магазинов с Batumi:")
                for idx, row in sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    product = row['PRODUCT_NAME']
                    quantity = row['QUANTITY']
                    group = row['GROUP_NAME']
                    print(f"  {store} | {date} | {product} | {quantity} шт | {group}")
                
                # Группируем по магазинам и датам
                grouped = sales.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                print("\nИтоговые продажи по магазинам с Batumi:")
                print("Магазин | Дата | Товары | Сумма")
                print("-" * 50)
                
                for idx, row in grouped.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    quantity = row['QUANTITY']
                    total_sum = row['TOTAL_SUM']
                    print(f"{store} | {date} | {quantity:.2f} | {total_sum:.2f}")
                
                return sales
            else:
                print("Нет продаж для магазинов с Batumi за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка проверки продаж: {e}")
        return None

def main():
    """Основная функция"""
    print("=== ПРОВЕРКА МАГАЗИНА BATUMIMALL ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Проверяем все магазины
    print("\n" + "="*50)
    print("ЭТАП 1: Все магазины в базе данных")
    print("="*50)
    
    stores = check_batumimall_store()
    
    # Этап 2: Проверяем продажи для магазинов с Batumi
    print("\n" + "="*50)
    print("ЭТАП 2: Продажи для магазинов с Batumi")
    print("="*50)
    
    sales = check_sales_for_batumimall("2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("="*50)

if __name__ == "__main__":
    main()

