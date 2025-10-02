#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск ВСЕХ пачек кофе, включая большие упаковки
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

def find_all_coffee_packages():
    """Находит ВСЕ пачки кофе, включая большие упаковки"""
    try:
        with DatabaseConnector() as db:
            print("=== ПОИСК ВСЕХ ПАЧЕК КОФЕ ===")
            
            # Ищем все товары, которые могут быть пачками кофе
            # Расширяем поиск по ключевым словам
            query = """
            SELECT DISTINCT
                G.ID,
                G.NAME,
                G.OWNER,
                GG.NAME as GROUP_NAME
            FROM Goods G
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE (
                G.NAME LIKE '%кофе%' OR
                G.NAME LIKE '%coffee%' OR
                G.NAME LIKE '%блазер%' OR
                G.NAME LIKE '%blaser%' OR
                G.NAME LIKE '%эспрессо%' OR
                G.NAME LIKE '%espresso%' OR
                G.NAME LIKE '%доппио%' OR
                G.NAME LIKE '%doppio%' OR
                G.NAME LIKE '%молотый%' OR
                G.NAME LIKE '%зерно%' OR
                G.NAME LIKE '%beans%' OR
                G.NAME LIKE '%ground%' OR
                G.NAME LIKE '%кг%' OR
                G.NAME LIKE '%kg%' OR
                G.NAME LIKE '%г%' OR
                G.NAME LIKE '%g%' OR
                G.NAME LIKE '%пачка%' OR
                G.NAME LIKE '%упак%' OR
                G.NAME LIKE '%пак%' OR
                G.NAME LIKE '%portion%' OR
                G.NAME LIKE '%порция%'
            )
            AND G.NAME NOT LIKE '%тоник%'
            AND G.NAME NOT LIKE '%tonic%'
            AND G.NAME NOT LIKE '%cold%'
            AND G.NAME NOT LIKE '%hot%'
            AND G.NAME NOT LIKE '%напиток%'
            AND G.NAME NOT LIKE '%drink%'
            ORDER BY G.NAME
            """
            
            products = db.execute_query(query)
            print(f"Найдено потенциальных пачек кофе: {len(products)}")
            
            if not products.empty:
                print("\nВсе потенциальные пачки кофе:")
                for idx, row in products.iterrows():
                    print(f"ID: {row['ID']}, Название: {row['NAME']}")
                    print(f"  OWNER: {row['OWNER']}, Группа: {row['GROUP_NAME']}")
                    print()
                
                # Категоризируем по размеру
                small_packages = []  # < 100g
                medium_packages = []  # 100g - 500g
                large_packages = []  # > 500g
                unknown_packages = []
                
                for idx, row in products.iterrows():
                    name = row['NAME']
                    weight = extract_weight_from_name(name)
                    
                    if weight > 0:
                        if weight < 0.1:  # < 100g
                            small_packages.append((row, weight))
                        elif weight < 0.5:  # 100g - 500g
                            medium_packages.append((row, weight))
                        else:  # > 500g
                            large_packages.append((row, weight))
                    else:
                        unknown_packages.append((row, 0))
                
                print(f"\n=== КАТЕГОРИЗАЦИЯ ПО РАЗМЕРУ ===")
                print(f"Маленькие пачки (< 100g): {len(small_packages)}")
                for pkg, weight in small_packages:
                    print(f"  {pkg['NAME']} - {weight*1000:.0f}g")
                
                print(f"\nСредние пачки (100g - 500g): {len(medium_packages)}")
                for pkg, weight in medium_packages:
                    print(f"  {pkg['NAME']} - {weight*1000:.0f}g")
                
                print(f"\nБольшие пачки (> 500g): {len(large_packages)}")
                for pkg, weight in large_packages:
                    print(f"  {pkg['NAME']} - {weight*1000:.0f}g")
                
                print(f"\nНеизвестный вес: {len(unknown_packages)}")
                for pkg, weight in unknown_packages:
                    print(f"  {pkg['NAME']}")
                
                return small_packages, medium_packages, large_packages, unknown_packages
            else:
                print("Пачки кофе не найдены")
                return None, None, None, None
                
    except Exception as e:
        logger.error(f"Ошибка поиска пачек кофе: {e}")
        return None, None, None, None

def extract_weight_from_name(product_name):
    """Извлекает вес из названия товара"""
    import re
    
    if not product_name:
        return 0
    
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
    
    return 0

def get_sales_for_packages(package_ids, start_date, end_date):
    """Получает продажи для найденных пачек"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ПРОДАЖИ ПАЧЕК КОФЕ ({start_date} - {end_date}) ===")
            
            if not package_ids:
                print("Нет пачек для анализа")
                return None
            
            # Создаем список ID пачек
            ids_str = ','.join([str(pkg[0]['ID']) for pkg in package_ids])
            
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
            print(f"Получено записей продаж: {len(sales)}")
            
            if not sales.empty:
                print("\nПродажи пачек кофе:")
                print(sales)
                
                # Рассчитываем веса
                sales['ITEM_WEIGHT'] = sales['PRODUCT_NAME'].apply(extract_weight_from_name)
                sales['TOTAL_WEIGHT'] = sales['QUANTITY'] * sales['ITEM_WEIGHT']
                
                print("\nРасчет веса:")
                for idx, row in sales.iterrows():
                    print(f"  {row['PRODUCT_NAME']}")
                    print(f"    Количество: {row['QUANTITY']}")
                    print(f"    Вес за единицу: {row['ITEM_WEIGHT']} кг")
                    print(f"    Общий вес: {row['TOTAL_WEIGHT']} кг")
                    print()
                
                # Группируем по магазинам и датам
                grouped = sales.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_WEIGHT': 'sum'
                }).reset_index()
                
                print("Итоговые килограммы по магазинам:")
                print(grouped)
                
                return grouped
            else:
                print("Нет продаж пачек кофе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения продаж пачек: {e}")
        return None

def main():
    """Основная функция"""
    print("=== ПОИСК ВСЕХ ПАЧЕК КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Находим все пачки кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск всех пачек кофе")
    print("="*50)
    
    small, medium, large, unknown = find_all_coffee_packages()
    
    # Этап 2: Анализируем продажи больших пачек
    print("\n" + "="*50)
    print("ЭТАП 2: Анализ продаж больших пачек")
    print("="*50)
    
    if large:
        print("Анализируем большие пачки...")
        large_sales = get_sales_for_packages(large, "2025-09-29", "2025-09-30")
    
    # Этап 3: Анализируем продажи средних пачек
    print("\n" + "="*50)
    print("ЭТАП 3: Анализ продаж средних пачек")
    print("="*50)
    
    if medium:
        print("Анализируем средние пачки...")
        medium_sales = get_sales_for_packages(medium, "2025-09-29", "2025-09-30")
    
    # Этап 4: Анализируем продажи маленьких пачек
    print("\n" + "="*50)
    print("ЭТАП 4: Анализ продаж маленьких пачек")
    print("="*50)
    
    if small:
        print("Анализируем маленькие пачки...")
        small_sales = get_sales_for_packages(small, "2025-09-29", "2025-09-30")
    
    print("\n" + "="*50)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

