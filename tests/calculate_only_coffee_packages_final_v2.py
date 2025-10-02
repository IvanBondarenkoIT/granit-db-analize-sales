#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный расчет ТОЛЬКО пачек кофе (исключая кофемашины и аксессуары)
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

def get_only_coffee_packages(start_date, end_date):
    """Получает ТОЛЬКО пачки кофе (исключая кофемашины и аксессуары)"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ТОЛЬКО ПАЧКИ КОФЕ ({start_date} - {end_date}) ===")
            
            # Ищем ТОЛЬКО пачки кофе
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
                    -- ТОЛЬКО пачки кофе
                    GG.NAME LIKE '%Coffee Blasecafe blend (250 g)%' OR
                    GG.NAME LIKE '%Coffee Blasercafe singl origin (250g)%' OR
                    GG.NAME LIKE '%Coffee Fresh%' OR
                    GG.NAME LIKE '%Coffee Blaser%'
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
            print(f"Получено записей пачек кофе: {len(sales)}")
            
            if not sales.empty:
                # Группируем по группам
                group_counts = sales.groupby(['GROUP_NAME']).size().reset_index(name='COUNT')
                print("\nПачки кофе по группам:")
                for idx, row in group_counts.iterrows():
                    print(f"  {row['GROUP_NAME']}: {row['COUNT']} записей")
                
                # Показываем примеры товаров
                print("\nПримеры пачек кофе:")
                for idx, row in sales.head(20).iterrows():
                    print(f"  {row['PRODUCT_NAME']} (Группа: {row['GROUP_NAME']})")
                
                return sales
            else:
                print("Нет пачек кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения пачек кофе: {e}")
        return None

def extract_weight_from_package_name(product_name):
    """Извлекает вес из названия пачки кофе"""
    import re
    
    if not product_name:
        return 0.25  # По умолчанию для пачек кофе
    
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
    
    return 0.25  # По умолчанию для пачек кофе

def calculate_packages_weight(sales_data):
    """Рассчитывает вес пачек кофе"""
    if sales_data is None or sales_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСА ПАЧЕК КОФЕ ===")
    
    # Добавляем расчет веса
    sales_data['ITEM_WEIGHT'] = sales_data['PRODUCT_NAME'].apply(extract_weight_from_package_name)
    sales_data['TOTAL_WEIGHT'] = sales_data['QUANTITY'] * sales_data['ITEM_WEIGHT']
    
    # Группируем по магазинам и датам
    grouped = sales_data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
        'QUANTITY': 'sum',
        'TOTAL_WEIGHT': 'sum',
        'TOTAL_SUM': 'sum'
    }).reset_index()
    
    print("Итоговые килограммы пачек кофе по магазинам:")
    print(grouped)
    
    return grouped

def compare_with_verification(packages_data):
    """Сравнивает с эталонными данными"""
    print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
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
            our_weight = row['TOTAL_WEIGHT']
            
            # Ищем эталонные данные
            if store in verification_data and date in verification_data[store]:
                ref_weight = verification_data[store][date]
                total_matches += 1
                
                diff = our_weight - ref_weight
                if abs(diff) < 0.1:
                    status = "OK"
                    good_matches += 1
                elif abs(diff) < 0.5:
                    status = "ХОРОШО"
                    good_matches += 1
                else:
                    status = "ПЛОХО"
                
                print(f"{store} | {date} | {our_weight:.2f} | {ref_weight:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_weight
                total_ref += ref_weight
            else:
                print(f"{store} | {date} | {our_weight:.2f} | НЕТ ДАННЫХ | - | -")
                total_our += our_weight
        
        # Общая статистика
        print(f"\n=== ОБЩАЯ СТАТИСТИКА ===")
        total_diff = total_our - total_ref
        print(f"Общий наш расчет: {total_our:.2f} кг")
        print(f"Общий эталон: {total_ref:.2f} кг")
        print(f"Общая разница: {total_diff:+.2f} кг")
        print(f"Хороших совпадений: {good_matches}/{total_matches}")
        
        if abs(total_diff) < 1.0:
            print("ОТЛИЧНО! Логика работает правильно!")
        elif abs(total_diff) < 2.0:
            print("ХОРОШО! Логика работает приемлемо")
        else:
            print("ПЛОХО! Нужна корректировка логики")

def main():
    """Основная функция"""
    print("=== ФИНАЛЬНЫЙ РАСЧЕТ ТОЛЬКО ПАЧЕК КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Получаем только пачки кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Только пачки кофе")
    print("="*50)
    
    sales_data = get_only_coffee_packages("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов")
    print("="*50)
    
    weights_data = calculate_packages_weight(sales_data)
    
    # Этап 3: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification(weights_data)
    
    print("\n" + "="*50)
    print("РАСЧЕТ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

