#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПОИСК ТОЛЬКО ПАЧЕК КОФЕ (не чашек) для расчета килограммов
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

def find_coffee_packages_only(start_date, end_date):
    """Находит ТОЛЬКО пачки кофе (не чашки)"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ПОИСК ТОЛЬКО ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            # Ищем ТОЛЬКО пачки кофе (товары с весом в названии)
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
                    -- Ищем товары с весом в названии (пачки кофе)
                    G.NAME LIKE '%250 g%' OR
                    G.NAME LIKE '%250г%' OR
                    G.NAME LIKE '%500 g%' OR
                    G.NAME LIKE '%500г%' OR
                    G.NAME LIKE '%1 kg%' OR
                    G.NAME LIKE '%1кг%' OR
                    G.NAME LIKE '%200 g%' OR
                    G.NAME LIKE '%200г%' OR
                    G.NAME LIKE '%125 g%' OR
                    G.NAME LIKE '%125г%' OR
                    G.NAME LIKE '%80 g%' OR
                    G.NAME LIKE '%80г%' OR
                    G.NAME LIKE '%0.25%' OR
                    G.NAME LIKE '%0.5%' OR
                    G.NAME LIKE '%0.2%' OR
                    G.NAME LIKE '%0.125%' OR
                    G.NAME LIKE '%0.08%'
                )
                AND (
                    -- Только кофе
                    G.NAME LIKE '%Coffee%' OR
                    G.NAME LIKE '%кофе%' OR
                    G.NAME LIKE '%Кофе%' OR
                    G.NAME LIKE '%Blaser%' OR
                    G.NAME LIKE '%Blasercafe%'
                )
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Найдено пачек кофе: {len(sales)}")
            
            if not sales.empty:
                print("\nНайденные пачки кофе:")
                for idx, row in sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    product = row['PRODUCT_NAME']
                    quantity = row['QUANTITY']
                    group = row['GROUP_NAME']
                    print(f"  {store} | {date} | {product} | {quantity} шт | {group}")
                
                return sales
            else:
                print("Нет пачек кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска пачек кофе: {e}")
        return None

def calculate_packages_weight_only(sales_data):
    """Рассчитывает вес ТОЛЬКО для пачек кофе"""
    if sales_data is None or sales_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСА ТОЛЬКО ПАЧЕК КОФЕ ===")
    
    # Логика: количество пачек = килограммы
    sales_data['TOTAL_WEIGHT_KG'] = sales_data['QUANTITY']
    
    # Группируем по магазинам и датам
    grouped = sales_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT_KG': 'sum',
        'TOTAL_SUM': 'sum'
    }).reset_index()
    
    print("\nИтоговые килограммы пачек кофе:")
    print("Магазин | Дата | Пачки | Килограммы | Сумма")
    print("-" * 60)
    
    for idx, row in grouped.iterrows():
        store = row['STORE_NAME']
        date = row['SALE_DATE'].strftime('%Y-%m-%d')
        packages = row['QUANTITY']
        kg = row['TOTAL_WEIGHT_KG']
        total_sum = row['TOTAL_SUM']
        print(f"{store} | {date} | {packages:.2f} | {kg:.2f} | {total_sum:.2f}")
    
    return grouped

def compare_with_verification_packages(packages_data):
    """Сравнивает пачки кофе с эталонными данными"""
    print("\n=== СРАВНЕНИЕ ПАЧЕК КОФЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
    # Эталонные данные
    verification_data = {
        'CityMall': {'2025-09-29': 1.25, '2025-09-30': 0.50},
        'DK Batumi': {'2025-09-29': 4.25, '2025-09-30': 3.25},
        'DK Paliashvili': {'2025-09-29': 0.75, '2025-09-30': 0.50},
        'EastPoint': {'2025-09-29': 0.25, '2025-09-30': 5.25}
    }
    
    if packages_data is not None and not packages_data.empty:
        print("\nСравнительная таблица:")
        print("Магазин | Дата | Наши пачки | Эталон | Разница | Статус")
        print("-" * 70)
        
        total_our = 0
        total_ref = 0
        good_matches = 0
        total_matches = 0
        
        for idx, row in packages_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            our_packages = row['TOTAL_WEIGHT_KG']
            
            # Ищем эталонные данные
            if store in verification_data and date in verification_data[store]:
                ref_packages = verification_data[store][date]
                total_matches += 1
                
                diff = our_packages - ref_packages
                if abs(diff) < 0.01:
                    status = "ОТЛИЧНО"
                    good_matches += 1
                elif abs(diff) < 0.1:
                    status = "ХОРОШО"
                    good_matches += 1
                else:
                    status = "ПЛОХО"
                
                print(f"{store} | {date} | {our_packages:.2f} | {ref_packages:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_packages
                total_ref += ref_packages
            else:
                print(f"{store} | {date} | {our_packages:.2f} | НЕТ ДАННЫХ | - | -")
                total_our += our_packages
        
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
    print("=== ПОИСК ТОЛЬКО ПАЧЕК КОФЕ ДЛЯ РАСЧЕТА КИЛОГРАММОВ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("ЛОГИКА: Ищем только пачки кофе (товары с весом в названии)")
    
    # Этап 1: Находим пачки кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск пачек кофе")
    print("="*50)
    
    packages_data = find_coffee_packages_only("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов")
    print("="*50)
    
    weights_data = calculate_packages_weight_only(packages_data)
    
    # Этап 3: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_packages(weights_data)
    
    print("\n" + "="*50)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

