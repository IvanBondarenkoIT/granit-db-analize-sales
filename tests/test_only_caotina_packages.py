#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТ ТОЛЬКО ПАЧЕК CAOTINA (НЕ НАПИТКИ)
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

def test_only_caotina_packages(start_date, end_date):
    """Тестирует только пачки Caotina (не напитки)"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ТЕСТ ТОЛЬКО ПАЧЕК CAOTINA ({start_date} - {end_date}) ===")
            
            # Ищем только пачки Caotina (package), не напитки
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
                    -- Пачки кофе с весом в названии
                    (
                        (G.NAME LIKE '%250 g%' OR G.NAME LIKE '%250г%' OR
                         G.NAME LIKE '%500 g%' OR G.NAME LIKE '%500г%' OR
                         G.NAME LIKE '%1 kg%' OR G.NAME LIKE '%1кг%' OR
                         G.NAME LIKE '%200 g%' OR G.NAME LIKE '%200г%' OR
                         G.NAME LIKE '%125 g%' OR G.NAME LIKE '%125г%' OR
                         G.NAME LIKE '%80 g%' OR G.NAME LIKE '%80г%' OR
                         G.NAME LIKE '%0.25%' OR G.NAME LIKE '%0.5%' OR
                         G.NAME LIKE '%0.2%' OR G.NAME LIKE '%0.125%' OR
                         G.NAME LIKE '%0.08%')
                        AND (G.NAME LIKE '%Coffee%' OR G.NAME LIKE '%кофе%' OR 
                             G.NAME LIKE '%Кофе%' OR G.NAME LIKE '%Blaser%' OR 
                             G.NAME LIKE '%Blasercafe%')
                    )
                    OR
                    -- ТОЛЬКО пачки Caotina (package), НЕ напитки
                    (
                        GG.NAME LIKE '%Caotina swiss chocolate drink (package)%'
                    )
                )
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Найдено товаров (пачки кофе + пачки Caotina): {len(sales)}")
            
            if not sales.empty:
                # Анализируем по группам
                group_sales = sales.groupby(['GROUP_NAME']).agg({
                    'QUANTITY': 'sum',
                    'TOTAL_SUM': 'sum'
                }).reset_index()
                
                print("\nПродажи по группам (пачки кофе + пачки Caotina):")
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
                
                print("\nИтоговые продажи (пачки кофе + пачки Caotina) по магазинам:")
                print("Магазин | Дата | Товары | Сумма")
                print("-" * 50)
                
                for idx, row in store_sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    quantity = row['QUANTITY']
                    total_sum = row['TOTAL_SUM']
                    print(f"{store} | {date} | {quantity:.2f} | {total_sum:.2f}")
                
                return store_sales
            else:
                print("Нет продаж товаров (пачки кофе + пачки Caotina) за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования пачек Caotina: {e}")
        return None

def compare_packages_with_verification(packages_data):
    """Сравнивает пачки с эталонными данными"""
    print("\n=== СРАВНЕНИЕ ПАЧЕК С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
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
            our_packages = row['QUANTITY']
            
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
    print("=== ТЕСТ ТОЛЬКО ПАЧЕК CAOTINA (НЕ НАПИТКИ) ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Тестируем только пачки Caotina
    packages_data = test_only_caotina_packages("2025-09-29", "2025-09-30")
    
    # Сравниваем с эталонными данными
    compare_packages_with_verification(packages_data)
    
    print("\n" + "="*50)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

