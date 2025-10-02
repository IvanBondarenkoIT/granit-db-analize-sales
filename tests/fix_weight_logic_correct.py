#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИСПРАВЛЕННАЯ логика расчета килограммов
Количество пачек = килограммы (не умножаем на вес пачки)
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

def test_corrected_weight_logic(start_date, end_date):
    """Тестирует ИСПРАВЛЕННУЮ логику расчета килограммов"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ИСПРАВЛЕННАЯ ЛОГИКА РАСЧЕТА КИЛОГРАММОВ ({start_date} - {end_date}) ===")
            
            # Используем оригинальный запрос для получения пачек кофе
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','24435','25546','25775','25777','25789') THEN GD.Source ELSE NULL END) AS MonoCup,
                SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') THEN GD.Source ELSE NULL END) AS BlendCup,
                SUM(CASE WHEN G.OWNER IN ('24491','21385') THEN GD.Source ELSE NULL END) AS CaotinaCup,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','24435','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385') THEN GD.Source ELSE NULL END) AS AllCup,
                SUM(D.SUMMA) as TOTAL_CASH
            FROM storzakazdt D 
            JOIN STORZDTGDS GD ON D.ID = GD.SZID 
            JOIN Goods G ON GD.GodsID = G.ID 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            LEFT JOIN goodsgroups GG ON G.owner = GG.id
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
            GROUP BY stgp.name, D.DAT_
            ORDER BY stgp.name, D.DAT_
            """
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей: {len(sales)}")
            
            if not sales.empty:
                # ИСПРАВЛЕННАЯ ЛОГИКА: Количество пачек = килограммы
                sales['TOTAL_WEIGHT_KG'] = sales['ALLCUP']  # Количество пачек = килограммы!
                
                print("\n=== РЕЗУЛЬТАТЫ С ИСПРАВЛЕННОЙ ЛОГИКОЙ ===")
                print("Магазин | Дата | Пачки (AllCup) | Килограммы | Общая касса")
                print("-" * 70)
                
                for idx, row in sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    cups = row['ALLCUP'] if pd.notna(row['ALLCUP']) else 0
                    kg = row['TOTAL_WEIGHT_KG'] if pd.notna(row['TOTAL_WEIGHT_KG']) else 0
                    cash = row['TOTAL_CASH'] if pd.notna(row['TOTAL_CASH']) else 0
                    
                    print(f"{store} | {date} | {cups:.2f} | {kg:.2f} | {cash:.2f}")
                
                return sales
            else:
                print("Нет данных за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования логики: {e}")
        return None

def compare_with_verification_corrected(sales_data):
    """Сравнивает ИСПРАВЛЕННЫЕ результаты с эталонными данными"""
    print("\n=== СРАВНЕНИЕ ИСПРАВЛЕННЫХ РЕЗУЛЬТАТОВ ===")
    
    # Эталонные данные
    verification_data = {
        'CityMall': {'2025-09-29': 1.25, '2025-09-30': 0.50},
        'DK Batumi': {'2025-09-29': 4.25, '2025-09-30': 3.25},
        'DK Paliashvili': {'2025-09-29': 0.75, '2025-09-30': 0.50},
        'EastPoint': {'2025-09-29': 0.25, '2025-09-30': 5.25}
    }
    
    if sales_data is not None and not sales_data.empty:
        print("\nСравнительная таблица:")
        print("Магазин | Дата | Наши кг | Эталон | Разница | Статус")
        print("-" * 60)
        
        total_our = 0
        total_ref = 0
        good_matches = 0
        total_matches = 0
        
        for idx, row in sales_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            our_kg = row['TOTAL_WEIGHT_KG'] if pd.notna(row['TOTAL_WEIGHT_KG']) else 0
            
            # Ищем эталонные данные
            if store in verification_data and date in verification_data[store]:
                ref_kg = verification_data[store][date]
                total_matches += 1
                
                diff = our_kg - ref_kg
                if abs(diff) < 0.01:
                    status = "ОТЛИЧНО"
                    good_matches += 1
                elif abs(diff) < 0.1:
                    status = "ХОРОШО"
                    good_matches += 1
                else:
                    status = "ПЛОХО"
                
                print(f"{store} | {date} | {our_kg:.2f} | {ref_kg:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_kg
                total_ref += ref_kg
            else:
                print(f"{store} | {date} | {our_kg:.2f} | НЕТ ДАННЫХ | - | -")
                total_our += our_kg
        
        # Общая статистика
        print(f"\n=== ОБЩАЯ СТАТИСТИКА ===")
        total_diff = total_our - total_ref
        print(f"Общий наш расчет: {total_our:.2f} кг")
        print(f"Общий эталон: {total_ref:.2f} кг")
        print(f"Общая разница: {total_diff:+.2f} кг")
        print(f"Хороших совпадений: {good_matches}/{total_matches}")
        
        if abs(total_diff) < 0.1:
            print("🎯 ОТЛИЧНО! Логика работает правильно!")
        elif abs(total_diff) < 1.0:
            print("✅ ХОРОШО! Логика работает приемлемо")
        else:
            print("❌ ПЛОХО! Нужна корректировка логики")

def main():
    """Основная функция"""
    print("=== ТЕСТ ИСПРАВЛЕННОЙ ЛОГИКИ РАСЧЕТА КИЛОГРАММОВ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("ЛОГИКА: Количество пачек = килограммы (не умножаем на вес пачки)")
    
    # Тестируем исправленную логику
    sales_data = test_corrected_weight_logic("2025-09-29", "2025-09-30")
    
    # Сравниваем с эталонными данными
    compare_with_verification_corrected(sales_data)
    
    print("\n" + "="*50)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    import pandas as pd
    main()
