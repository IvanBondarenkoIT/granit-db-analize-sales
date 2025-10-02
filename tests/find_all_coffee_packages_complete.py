#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОИСК ВСЕХ ПАЧЕК КОФЕ (включая без веса в названии)
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

def find_all_coffee_packages_complete(start_date, end_date):
    """Находит ВСЕ пачки кофе (включая без веса в названии)"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ПОИСК ВСЕХ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            # Ищем ВСЕ товары кофе (не напитки)
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
                    -- Ищем ВСЕ товары кофе
                    GG.NAME LIKE '%Coffee%' OR
                    GG.NAME LIKE '%кофе%' OR
                    GG.NAME LIKE '%Кофе%' OR
                    GG.NAME LIKE '%Blaser%' OR
                    GG.NAME LIKE '%Blasercafe%' OR
                    G.NAME LIKE '%Coffee%' OR
                    G.NAME LIKE '%кофе%' OR
                    G.NAME LIKE '%Кофе%' OR
                    G.NAME LIKE '%Blaser%' OR
                    G.NAME LIKE '%Blasercafe%'
                )
                AND NOT (
                    -- Исключаем напитки
                    GG.NAME LIKE '%espresso%' OR
                    GG.NAME LIKE '%Cold%' OR
                    GG.NAME LIKE '%Tonic%' OR
                    GG.NAME LIKE '%Smoothie%' OR
                    GG.NAME LIKE '%Tropic%' OR
                    GG.NAME LIKE '%DRINKS%' OR
                    -- Исключаем кофемашины и аксессуары
                    GG.NAME LIKE '%makers%' OR
                    GG.NAME LIKE '%Gaggia%' OR
                    GG.NAME LIKE '%Macap%' OR
                    GG.NAME LIKE '%Saeco%' OR
                    GG.NAME LIKE '%Handpresso%' OR
                    GG.NAME LIKE '%Melitta%' OR
                    GG.NAME LIKE '%Delonghi%' OR
                    GG.NAME LIKE '%accessories%' OR
                    GG.NAME LIKE '%Tech%' OR
                    -- Исключаем расходники и еду
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
            print(f"Найдено товаров кофе: {len(sales)}")
            
            if not sales.empty:
                # Анализируем группы
                group_counts = sales.groupby(['GROUP_NAME']).size().reset_index(name='COUNT')
                print("\nТовары кофе по группам:")
                for idx, row in group_counts.iterrows():
                    print(f"  {row['GROUP_NAME']}: {row['COUNT']} записей")
                
                # Анализируем товары с весом в названии
                weight_products = sales[sales['PRODUCT_NAME'].str.contains(r'\d+[.,]?\d*\s*[кгgг]', case=False, na=False)]
                print(f"\nТовары с весом в названии: {len(weight_products)}")
                
                # Анализируем товары без веса в названии
                no_weight_products = sales[~sales['PRODUCT_NAME'].str.contains(r'\d+[.,]?\d*\s*[кгgг]', case=False, na=False)]
                print(f"Товары без веса в названии: {len(no_weight_products)}")
                
                if len(no_weight_products) > 0:
                    print("\nТовары без веса в названии:")
                    for idx, row in no_weight_products.iterrows():
                        store = row['STORE_NAME']
                        date = row['SALE_DATE'].strftime('%Y-%m-%d')
                        product = row['PRODUCT_NAME']
                        quantity = row['QUANTITY']
                        group = row['GROUP_NAME']
                        print(f"  {store} | {date} | {product} | {quantity} шт | {group}")
                
                return sales
            else:
                print("Нет товаров кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска товаров кофе: {e}")
        return None

def calculate_all_coffee_weight(sales_data):
    """Рассчитывает вес для ВСЕХ товаров кофе"""
    if sales_data is None or sales_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСА ВСЕХ ТОВАРОВ КОФЕ ===")
    
    # Логика: количество товаров = килограммы
    sales_data['TOTAL_WEIGHT_KG'] = sales_data['QUANTITY']
    
    # Группируем по магазинам и датам
    grouped = sales_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT_KG': 'sum',
        'TOTAL_SUM': 'sum'
    }).reset_index()
    
    print("\nИтоговые килограммы всех товаров кофе:")
    print("Магазин | Дата | Товары | Килограммы | Сумма")
    print("-" * 60)
    
    for idx, row in grouped.iterrows():
        store = row['STORE_NAME']
        date = row['SALE_DATE'].strftime('%Y-%m-%d')
        items = row['QUANTITY']
        kg = row['TOTAL_WEIGHT_KG']
        total_sum = row['TOTAL_SUM']
        print(f"{store} | {date} | {items:.2f} | {kg:.2f} | {total_sum:.2f}")
    
    return grouped

def compare_with_verification_all_coffee(all_coffee_data):
    """Сравнивает все товары кофе с эталонными данными"""
    print("\n=== СРАВНЕНИЕ ВСЕХ ТОВАРОВ КОФЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
    # Эталонные данные
    verification_data = {
        'CityMall': {'2025-09-29': 1.25, '2025-09-30': 0.50},
        'DK Batumi': {'2025-09-29': 4.25, '2025-09-30': 3.25},
        'DK Paliashvili': {'2025-09-29': 0.75, '2025-09-30': 0.50},
        'EastPoint': {'2025-09-29': 0.25, '2025-09-30': 5.25}
    }
    
    if all_coffee_data is not None and not all_coffee_data.empty:
        print("\nСравнительная таблица:")
        print("Магазин | Дата | Наши товары | Эталон | Разница | Статус")
        print("-" * 70)
        
        total_our = 0
        total_ref = 0
        good_matches = 0
        total_matches = 0
        
        for idx, row in all_coffee_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            our_items = row['TOTAL_WEIGHT_KG']
            
            # Ищем эталонные данные
            if store in verification_data and date in verification_data[store]:
                ref_items = verification_data[store][date]
                total_matches += 1
                
                diff = our_items - ref_items
                if abs(diff) < 0.01:
                    status = "ОТЛИЧНО"
                    good_matches += 1
                elif abs(diff) < 0.1:
                    status = "ХОРОШО"
                    good_matches += 1
                else:
                    status = "ПЛОХО"
                
                print(f"{store} | {date} | {our_items:.2f} | {ref_items:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_items
                total_ref += ref_items
            else:
                print(f"{store} | {date} | {our_items:.2f} | НЕТ ДАННЫХ | - | -")
                total_our += our_items
        
        # Общая статистика
        print(f"\n=== ОБЩАЯ СТАТИСТИКА ===")
        total_diff = total_our - total_ref
        print(f"Общий наш расчет: {total_our:.2f} кг")
        print(f"Общий эталон: {total_ref:.2f} кг")
        print(f"Общая разница: {total_diff:+.2f} кг")
        print(f"Хороших совпадений: {good_matches}/{total_matches}")
        
        if abs(total_diff) < 0.1:
            print("ОТЛИЧНО! Логика работает правильно!")
        elif abs(total_diff) < 1.0:
            print("ХОРОШО! Логика работает приемлемо")
        else:
            print("ПЛОХО! Нужна корректировка логики")

def main():
    """Основная функция"""
    print("=== ПОИСК ВСЕХ ТОВАРОВ КОФЕ ДЛЯ РАСЧЕТА КИЛОГРАММОВ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("ЛОГИКА: Ищем ВСЕ товары кофе (включая без веса в названии)")
    
    # Этап 1: Находим все товары кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск всех товаров кофе")
    print("="*50)
    
    all_coffee_data = find_all_coffee_packages_complete("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов")
    print("="*50)
    
    weights_data = calculate_all_coffee_weight(all_coffee_data)
    
    # Этап 3: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_all_coffee(weights_data)
    
    print("\n" + "="*50)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()