#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Анализ оригинального запроса
Изучаем как правильно считать чашки, килограммы и суммы
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

def analyze_original_query(start_date, end_date):
    """Анализирует оригинальный запрос"""
    try:
        with DatabaseConnector() as db:
            print(f"=== АНАЛИЗ ОРИГИНАЛЬНОГО ЗАПРОСА ({start_date} - {end_date}) ===")
            
            # Оригинальный запрос
            query = """
            SELECT 
                stgp.name, 
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','24435','25546','25775','25777','25789') THEN GD.Source ELSE NULL END) AS MonoCup,
                SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') THEN GD.Source ELSE NULL END) AS BlendCup,
                SUM(CASE WHEN G.OWNER IN ('24491','21385') THEN GD.Source ELSE NULL END) AS CaotinaCup,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','24435','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385') THEN GD.Source ELSE NULL END) AS AllCup,
                D.DAT_
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
            
            result = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей: {len(result)}")
            
            if not result.empty:
                print("\nРезультаты оригинального запроса:")
                print(result)
                
                # Анализируем данные
                print("\n=== АНАЛИЗ ДАННЫХ ===")
                for idx, row in result.iterrows():
                    store = row['NAME']
                    date = row['DAT_']
                    mono = row['MONOCUP'] or 0
                    blend = row['BLENDCUP'] or 0
                    caotina = row['CAOTINACUP'] or 0
                    all_cup = row['ALLCUP'] or 0
                    
                    print(f"\n{store} ({date}):")
                    print(f"  MonoCup: {mono}")
                    print(f"  BlendCup: {blend}")
                    print(f"  CaotinaCup: {caotina}")
                    print(f"  AllCup: {all_cup}")
                    print(f"  Проверка: {mono + blend + caotina} = {all_cup}")
                
                return result
            else:
                print("Нет данных по оригинальному запросу")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа оригинального запроса: {e}")
        return None

def calculate_weights_from_original_data(original_data):
    """Рассчитывает веса на основе оригинальных данных"""
    if original_data is None or original_data.empty:
        return None
    
    print("\n=== РАСЧЕТ ВЕСОВ НА ОСНОВЕ ОРИГИНАЛЬНЫХ ДАННЫХ ===")
    
    # Добавляем расчет веса
    original_data['MONO_WEIGHT'] = original_data['MONOCUP'] * 0.25
    original_data['BLEND_WEIGHT'] = original_data['BLENDCUP'] * 0.25
    original_data['CAOTINA_WEIGHT'] = original_data['CAOTINACUP'] * 0.25
    original_data['TOTAL_WEIGHT'] = original_data['ALLCUP'] * 0.25
    
    print("Расчет веса (предполагаем 0.25 кг за чашку):")
    print(original_data[['NAME', 'DAT_', 'MONOCUP', 'BLENDCUP', 'CAOTINACUP', 'ALLCUP', 'TOTAL_WEIGHT']])
    
    return original_data

def get_total_sales_amount(start_date, end_date):
    """Получает общую сумму продаж (касса)"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== ОБЩАЯ СУММА ПРОДАЖ ({start_date} - {end_date}) ===")
            
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(D.SUMMA) as TOTAL_CASH
            FROM storzakazdt D 
            JOIN storgrp stgp ON D.storgrpid = stgp.id 
            WHERE D.STORGRPID IN ('27','43','44','46') 
                AND D.CSDTKTHBID IN ('1', '2', '3','5') 
                AND D.DAT_ >= ? AND D.DAT_ <= ?
                AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
            GROUP BY stgp.name, D.DAT_
            ORDER BY stgp.name, D.DAT_
            """
            
            result = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей общей кассы: {len(result)}")
            
            if not result.empty:
                print("\nОбщая касса:")
                print(result)
                return result
            else:
                print("Нет данных общей кассы")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения общей кассы: {e}")
        return None

def compare_with_verification_data(original_data, cash_data):
    """Сравнивает с эталонными данными"""
    try:
        import pandas as pd
        
        print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
        
        # Загружаем эталонные данные
        excel_file = "data/данные для сверки.xlsx"
        cash_verification = pd.read_excel(excel_file, sheet_name="Общая касса")
        kg_verification = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        
        print("\nЭталонные данные - Общая касса:")
        print(cash_verification)
        
        print("\nЭталонные данные - Килограммы:")
        print(kg_verification)
        
        if original_data is not None and not original_data.empty:
            print("\nНаши данные - Чашки и расчетный вес:")
            print(original_data[['NAME', 'DAT_', 'ALLCUP', 'TOTAL_WEIGHT']])
        
        if cash_data is not None and not cash_data.empty:
            print("\nНаши данные - Общая касса:")
            print(cash_data)
        
        # Создаем сводную таблицу
        print("\n=== СВОДНАЯ ТАБЛИЦА СРАВНЕНИЯ ===")
        print("Магазин | Дата | Чашки | Расчетный вес | Эталон вес | Общая касса | Эталон касса")
        print("-" * 80)
        
        if original_data is not None and not original_data.empty:
            for idx, row in original_data.iterrows():
                store = row['NAME']
                date = row['DAT_'].strftime('%Y-%m-%d')
                cups = row['ALLCUP'] or 0
                calc_weight = row['TOTAL_WEIGHT'] or 0
                
                # Ищем эталонные данные
                store_row_kg = kg_verification[kg_verification['Unnamed: 0'] == store]
                store_row_cash = cash_verification[cash_verification['Unnamed: 0'] == store]
                
                if not store_row_kg.empty:
                    if date == '2025-09-29':
                        ref_weight = store_row_kg.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_weight = store_row_kg.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_weight = 0
                else:
                    ref_weight = 0
                
                if not store_row_cash.empty:
                    if date == '2025-09-29':
                        ref_cash = store_row_cash.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_cash = store_row_cash.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_cash = 0
                else:
                    ref_cash = 0
                
                # Ищем нашу кассу
                our_cash = 0
                if cash_data is not None and not cash_data.empty:
                    cash_row = cash_data[(cash_data['STORE_NAME'] == store) & (cash_data['SALE_DATE'].dt.strftime('%Y-%m-%d') == date)]
                    if not cash_row.empty:
                        our_cash = cash_row.iloc[0]['TOTAL_CASH']
                
                print(f"{store} | {date} | {cups} | {calc_weight:.2f} | {ref_weight} | {our_cash:.2f} | {ref_cash}")
        
    except Exception as e:
        logger.error(f"Ошибка сравнения с эталонными данными: {e}")

def main():
    """Основная функция"""
    print("=== АНАЛИЗ ОРИГИНАЛЬНОГО ЗАПРОСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Анализируем оригинальный запрос
    print("\n" + "="*50)
    print("ЭТАП 1: Анализ оригинального запроса")
    print("="*50)
    
    original_data = analyze_original_query("2025-09-29", "2025-09-30")
    
    # Этап 2: Рассчитываем веса
    print("\n" + "="*50)
    print("ЭТАП 2: Расчет весов на основе оригинальных данных")
    print("="*50)
    
    weights_data = calculate_weights_from_original_data(original_data)
    
    # Этап 3: Получаем общую кассу
    print("\n" + "="*50)
    print("ЭТАП 3: Получение общей кассы")
    print("="*50)
    
    cash_data = get_total_sales_amount("2025-09-29", "2025-09-30")
    
    # Этап 4: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 4: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_data(original_data, cash_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

