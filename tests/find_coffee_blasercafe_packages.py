#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск пачек кофе из группы "Coffee Blasercafe"
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

def find_coffee_blasercafe_group():
    """Находит группу Coffee Blasercafe и её товары"""
    try:
        with DatabaseConnector() as db:
            print("=== ПОИСК ГРУППЫ COFFEE BLASERCAFE ===")
            
            # 1. Находим группу Coffee Blasercafe
            query1 = """
            SELECT ID, NAME, PARENT_ID
            FROM goodsgroups 
            WHERE NAME LIKE '%Coffee%' OR NAME LIKE '%Blasercafe%' OR NAME LIKE '%кофе%'
            ORDER BY NAME
            """
            
            groups = db.execute_query(query1)
            print("Найденные группы кофе:")
            for idx, row in groups.iterrows():
                print(f"  ID: {row['ID']}, Название: {row['NAME']}, Родитель: {row['PARENT_ID']}")
            
            # 2. Находим товары из группы Coffee Blasercafe
            query2 = """
            SELECT DISTINCT
                G.ID,
                G.NAME,
                G.OWNER,
                GG.NAME as GROUP_NAME,
                GG.ID as GROUP_ID
            FROM Goods G
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE GG.NAME LIKE '%Coffee%' OR GG.NAME LIKE '%Blasercafe%' OR GG.NAME LIKE '%кофе%'
            ORDER BY G.NAME
            """
            
            products = db.execute_query(query2)
            print(f"\nНайдено товаров в группах кофе: {len(products)}")
            
            if not products.empty:
                # Группируем по группам
                group_counts = products.groupby(['GROUP_NAME', 'GROUP_ID']).size().reset_index(name='COUNT')
                print("\nТовары по группам:")
                for idx, row in group_counts.iterrows():
                    print(f"  Группа: {row['GROUP_NAME']} (ID: {row['GROUP_ID']}) - {row['COUNT']} товаров")
                
                print("\nВсе товары кофе:")
                for idx, row in products.iterrows():
                    print(f"  {row['NAME']} (Группа: {row['GROUP_NAME']})")
                
                return products
            else:
                print("Товары кофе не найдены")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска группы кофе: {e}")
        return None

def get_coffee_packages_sales(package_ids, start_date, end_date):
    """Получает продажи пачек кофе"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПРОДАЖИ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            if not package_ids or package_ids.empty:
                print("Нет пачек кофе для анализа")
                return None
            
            # Создаем список ID пачек
            ids_str = ','.join([str(pkg['ID']) for pkg in package_ids.itertuples()])
            
            query = f"""
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                G.NAME as PRODUCT_NAME,
                GD.SOURCE as QUANTITY,
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
                AND G.ID IN ({ids_str})
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей продаж пачек: {len(sales)}")
            
            if not sales.empty:
                print("\nПродажи пачек кофе:")
                print(sales)
                
                return sales
            else:
                print("Нет продаж пачек кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения продаж пачек: {e}")
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
    print("=== ПОИСК ПАЧЕК КОФЕ ИЗ ГРУППЫ COFFEE BLASERCAFE ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Находим группу Coffee Blasercafe
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск группы Coffee Blasercafe")
    print("="*50)
    
    packages = find_coffee_blasercafe_group()
    
    # Этап 2: Получаем продажи пачек
    print("\n" + "="*50)
    print("ЭТАП 2: Продажи пачек кофе")
    print("="*50)
    
    sales_data = get_coffee_packages_sales(packages, "2025-09-29", "2025-09-30")
    
    # Этап 3: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 3: Расчет весов пачек")
    print("="*50)
    
    weights_data = calculate_packages_weight(sales_data)
    
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

