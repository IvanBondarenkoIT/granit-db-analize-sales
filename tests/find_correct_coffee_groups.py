#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Поиск правильных групп кофе для расчета килограммов
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

def find_correct_coffee_groups(start_date, end_date):
    """Находит правильные группы кофе для расчета килограммов"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ПОИСК ПРАВИЛЬНЫХ ГРУПП КОФЕ ({start_date} - {end_date}) ===")
            
            # Сначала найдем ВСЕ группы кофе, которые есть в продажах
            query1 = """
            SELECT DISTINCT
                GG.NAME as GROUP_NAME,
                GG.ID as GROUP_ID,
                COUNT(*) as SALES_COUNT
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
                AND GG.NAME IS NOT NULL
                AND (GG.NAME LIKE '%Coffee%' OR GG.NAME LIKE '%кофе%' OR GG.NAME LIKE '%Кофе%')
            GROUP BY GG.NAME, GG.ID
            ORDER BY SALES_COUNT DESC
            """
            
            groups = db.execute_query(query1, (start_date, end_date))
            print(f"Найдено групп кофе в продажах: {len(groups)}")
            
            if not groups.empty:
                print("\nГруппы кофе по количеству продаж:")
                for idx, row in groups.iterrows():
                    print(f"  {row['GROUP_NAME']} (ID: {row['GROUP_ID']}): {row['SALES_COUNT']} продаж")
                
                # Теперь найдем продажи из этих групп
                group_ids = groups['GROUP_ID'].tolist()
                ids_str = ','.join([str(gid) for gid in group_ids])
                
                query2 = f"""
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
                    AND G.owner IN ({ids_str})
                ORDER BY stgp.name, D.DAT_, G.NAME
                """
                
                sales = db.execute_query(query2, (start_date, end_date))
                print(f"\nПолучено записей продаж кофе: {len(sales)}")
                
                if not sales.empty:
                    # Группируем по группам
                    group_counts = sales.groupby(['GROUP_NAME']).size().reset_index(name='COUNT')
                    print("\nПродажи по группам кофе:")
                    for idx, row in group_counts.iterrows():
                        print(f"  {row['GROUP_NAME']}: {row['COUNT']} записей")
                    
                    return sales
                else:
                    print("Нет продаж кофе за указанный период")
                    return None
            else:
                print("Группы кофе не найдены")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка поиска групп кофе: {e}")
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
    print("=== ПОИСК ПРАВИЛЬНЫХ ГРУПП КОФЕ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Находим правильные группы кофе
    print("\n" + "="*50)
    print("ЭТАП 1: Поиск правильных групп кофе")
    print("="*50)
    
    sales_data = find_correct_coffee_groups("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов пачек")
    print("="*50)
    
    weights_data = calculate_packages_weight(sales_data)
    
    # Этап 3: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification(weights_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

