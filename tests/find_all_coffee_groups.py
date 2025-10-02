#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОИСК ВСЕХ ГРУПП ТОВАРОВ, СВЯЗАННЫХ С КОФЕ
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

def find_all_coffee_groups():
    """Находит ВСЕ группы товаров, связанные с кофе"""
    try:
        with DatabaseConnector() as db:
            print("=== ПОИСК ВСЕХ ГРУПП ТОВАРОВ, СВЯЗАННЫХ С КОФЕ ===")
            
            # Ищем все группы товаров, содержащие кофе
            query = """
            SELECT DISTINCT
                GG.ID as GROUP_ID,
                GG.NAME as GROUP_NAME,
                COUNT(G.ID) as PRODUCT_COUNT
            FROM goodsgroups GG
            LEFT JOIN Goods G ON GG.ID = G.OWNER
            WHERE (
                GG.NAME LIKE '%Coffee%' OR
                GG.NAME LIKE '%кофе%' OR
                GG.NAME LIKE '%Кофе%' OR
                GG.NAME LIKE '%Blaser%' OR
                GG.NAME LIKE '%Blasercafe%' OR
                GG.NAME LIKE '%coffee%' OR
                GG.NAME LIKE '%COFFEE%'
            )
            GROUP BY GG.ID, GG.NAME
            ORDER BY GG.NAME
            """
            
            groups = db.execute_query(query)
            print(f"Найдено групп товаров кофе: {len(groups)}")
            
            if not groups.empty:
                print("\nВсе группы товаров кофе:")
                for idx, row in groups.iterrows():
                    group_id = row['GROUP_ID']
                    group_name = row['GROUP_NAME']
                    product_count = row['PRODUCT_COUNT']
                    print(f"  ID: {group_id} | {group_name} | Товаров: {product_count}")
                
                return groups
            else:
                print("Нет групп товаров кофе")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска групп кофе: {e}")
        return None

def find_products_in_coffee_groups():
    """Находит товары во всех группах кофе"""
    try:
        with DatabaseConnector() as db:
            print("\n=== ТОВАРЫ ВО ВСЕХ ГРУППАХ КОФЕ ===")
            
            # Ищем все товары в группах кофе
            query = """
            SELECT 
                GG.ID as GROUP_ID,
                GG.NAME as GROUP_NAME,
                G.ID as PRODUCT_ID,
                G.NAME as PRODUCT_NAME,
                G.OWNER as PRODUCT_OWNER
            FROM goodsgroups GG
            JOIN Goods G ON GG.ID = G.OWNER
            WHERE (
                GG.NAME LIKE '%Coffee%' OR
                GG.NAME LIKE '%кофе%' OR
                GG.NAME LIKE '%Кофе%' OR
                GG.NAME LIKE '%Blaser%' OR
                GG.NAME LIKE '%Blasercafe%' OR
                GG.NAME LIKE '%coffee%' OR
                GG.NAME LIKE '%COFFEE%'
            )
            ORDER BY GG.NAME, G.NAME
            """
            
            products = db.execute_query(query)
            print(f"Найдено товаров в группах кофе: {len(products)}")
            
            if not products.empty:
                # Группируем по группам
                group_products = products.groupby(['GROUP_NAME']).size().reset_index(name='COUNT')
                print("\nТовары по группам кофе:")
                for idx, row in group_products.iterrows():
                    group_name = row['GROUP_NAME']
                    count = row['COUNT']
                    print(f"  {group_name}: {count} товаров")
                
                # Показываем примеры товаров
                print("\nПримеры товаров в группах кофе:")
                for idx, row in products.head(20).iterrows():
                    group_name = row['GROUP_NAME']
                    product_name = row['PRODUCT_NAME']
                    print(f"  {group_name}: {product_name}")
                
                return products
            else:
                print("Нет товаров в группах кофе")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска товаров в группах кофе: {e}")
        return None

def test_sales_for_all_coffee_groups(start_date, end_date):
    """Тестирует продажи для всех групп кофе"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПРОДАЖИ ДЛЯ ВСЕХ ГРУПП КОФЕ ({start_date} - {end_date}) ===")
            
            # Ищем продажи для всех групп кофе
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
                AND (
                    GG.NAME LIKE '%Coffee%' OR
                    GG.NAME LIKE '%кофе%' OR
                    GG.NAME LIKE '%Кофе%' OR
                    GG.NAME LIKE '%Blaser%' OR
                    GG.NAME LIKE '%Blasercafe%' OR
                    GG.NAME LIKE '%coffee%' OR
                    GG.NAME LIKE '%COFFEE%'
                )
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Найдено продаж товаров кофе: {len(sales)}")
            
            if not sales.empty:
                # Анализируем по группам
                group_sales = sales.groupby(['GROUP_NAME']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                print("\nПродажи по группам кофе:")
                for idx, row in group_sales.iterrows():
                    group_name = row['GROUP_NAME']
                    quantity = row['QUANTITY']
                    total_sum = row['TOTAL_SUM']
                    print(f"  {group_name}: {quantity:.2f} шт, {total_sum:.2f} руб")
                
                # Группируем по магазинам и датам
                store_sales = sales.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                print("\nИтоговые продажи по магазинам:")
                print("Магазин | Дата | Товары | Сумма")
                print("-" * 50)
                
                for idx, row in store_sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    quantity = row['QUANTITY']
                    total_sum = row['TOTAL_SUM']
                    print(f"{store} | {date} | {quantity:.2f} | {total_sum:.2f}")
                
                return sales
            else:
                print("Нет продаж товаров кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования продаж: {e}")
        return None

def main():
    """Основная функция"""
    print("=== ПОИСК ВСЕХ ГРУПП ТОВАРОВ, СВЯЗАННЫХ С КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Находим все группы кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск групп кофе")
    print("="*50)
    
    groups = find_all_coffee_groups()
    
    # Этап 2: Находим товары в группах кофе
    print("\n" + "="*50)
    print("ЭТАП 2: Товары в группах кофе")
    print("="*50)
    
    products = find_products_in_coffee_groups()
    
    # Этап 3: Тестируем продажи для всех групп кофе
    print("\n" + "="*50)
    print("ЭТАП 3: Продажи для всех групп кофе")
    print("="*50)
    
    sales = test_sales_for_all_coffee_groups("2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

