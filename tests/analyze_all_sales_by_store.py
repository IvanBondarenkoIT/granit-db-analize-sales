#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ всех продаж по магазинам за период
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

def analyze_all_sales_by_store(start_date, end_date):
    """Анализирует все продажи по магазинам за период"""
    try:
        with DatabaseConnector() as db:
            print(f"=== АНАЛИЗ ВСЕХ ПРОДАЖ ПО МАГАЗИНАМ ({start_date} - {end_date}) ===")
            
            # 1. Получаем все продажи по магазинам
            query1 = """
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
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query1, (start_date, end_date))
            print(f"Всего записей продаж: {len(sales)}")
            
            if not sales.empty:
                # 2. Анализируем по магазинам
                print("\n=== ПРОДАЖИ ПО МАГАЗИНАМ ===")
                store_stats = sales.groupby('STORE_NAME').agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum',
                    'PRODUCT_NAME': 'count'
                }).reset_index()
                store_stats.columns = ['STORE_NAME', 'TOTAL_QUANTITY', 'TOTAL_SUM', 'UNIQUE_PRODUCTS']
                
                for idx, row in store_stats.iterrows():
                    print(f"\n{row['STORE_NAME']}:")
                    print(f"  Всего товаров: {row['UNIQUE_PRODUCTS']}")
                    print(f"  Общее количество: {row['TOTAL_QUANTITY']}")
                    print(f"  Общая сумма: {row['TOTAL_SUM']:.2f}")
                
                # 3. Анализируем группы товаров
                print("\n=== ГРУППЫ ТОВАРОВ В ПРОДАЖАХ ===")
                group_stats = sales.groupby(['GROUP_NAME', 'GROUP_ID']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum',
                    'PRODUCT_NAME': 'count'
                }).reset_index()
                group_stats.columns = ['GROUP_NAME', 'GROUP_ID', 'TOTAL_QUANTITY', 'TOTAL_SUM', 'UNIQUE_PRODUCTS']
                group_stats = group_stats.sort_values('TOTAL_SUM', ascending=False)
                
                print("Топ-20 групп по сумме продаж:")
                for idx, row in group_stats.head(20).iterrows():
                    print(f"  {row['GROUP_NAME']} (ID: {row['GROUP_ID']})")
                    print(f"    Товаров: {row['UNIQUE_PRODUCTS']}, Количество: {row['TOTAL_QUANTITY']}, Сумма: {row['TOTAL_SUM']:.2f}")
                
                # 4. Фильтруем только группы кофе
                print("\n=== ГРУППЫ КОФЕ В ПРОДАЖАХ ===")
                coffee_groups = group_stats[
                    group_stats['GROUP_NAME'].str.contains('Coffee|кофе|Кофе|Blaser|Blasercafe', case=False, na=False)
                ]
                
                if not coffee_groups.empty:
                    print("Группы кофе в продажах:")
                    for idx, row in coffee_groups.iterrows():
                        print(f"  {row['GROUP_NAME']} (ID: {row['GROUP_ID']})")
                        print(f"    Товаров: {row['UNIQUE_PRODUCTS']}, Количество: {row['TOTAL_QUANTITY']}, Сумма: {row['TOTAL_SUM']:.2f}")
                    
                    # 5. Показываем примеры товаров из групп кофе
                    print("\n=== ПРИМЕРЫ ТОВАРОВ ИЗ ГРУПП КОФЕ ===")
                    coffee_sales = sales[
                        sales['GROUP_NAME'].str.contains('Coffee|кофе|Кофе|Blaser|Blasercafe', case=False, na=False)
                    ]
                    
                    for group_name in coffee_groups['GROUP_NAME'].unique():
                        group_products = coffee_sales[coffee_sales['GROUP_NAME'] == group_name]
                        print(f"\nГруппа: {group_name}")
                        print(f"Товаров в группе: {len(group_products)}")
                        
                        # Показываем первые 5 товаров
                        for idx, row in group_products.head(5).iterrows():
                            print(f"  {row['PRODUCT_NAME']} - {row['QUANTITY']} шт, {row['TOTAL_SUM']:.2f} руб")
                        
                        if len(group_products) > 5:
                            print(f"  ... и еще {len(group_products) - 5} товаров")
                
                return sales
            else:
                print("Нет продаж за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа продаж: {e}")
        return None

def main():
    """Основная функция"""
    print("=== АНАЛИЗ ВСЕХ ПРОДАЖ ПО МАГАЗИНАМ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Анализируем все продажи
    print("\n" + "="*50)
    print("АНАЛИЗ ВСЕХ ПРОДАЖ")
    print("="*50)
    
    sales_data = analyze_all_sales_by_store("2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

