#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА СУММ ПРОДАЖ
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_connector import DatabaseConnector
from logger_config import setup_logger

# Настраиваем логирование
logger = setup_logger(__name__)

def load_verification_cash_data():
    """Загружает эталонные данные по общей кассе"""
    try:
        print("=== ЗАГРУЗКА ЭТАЛОННЫХ ДАННЫХ ПО ОБЩЕЙ КАССЕ ===")
        
        excel_file = "data/данные для сверки.xlsx"
        
        if not os.path.exists(excel_file):
            print(f"Файл {excel_file} не найден!")
            return None
        
        # Читаем вкладку "Общая касса"
        cash_data = pd.read_excel(excel_file, sheet_name="Общая касса")
        print("Эталонные данные по общей кассе:")
        print(cash_data)
        
        # Преобразуем в удобный формат
        verification_cash = {}
        for idx, row in cash_data.iterrows():
            store = row['Unnamed: 0']
            if pd.notna(store):
                verification_cash[store] = {
                    '2025-09-29': row[datetime(2025, 9, 29)] if pd.notna(row[datetime(2025, 9, 29)]) else 0,
                    '2025-09-30': row[datetime(2025, 9, 30)] if pd.notna(row[datetime(2025, 9, 30)]) else 0
                }
        
        print("\nЭталонные суммы по магазинам:")
        for store, dates in verification_cash.items():
            print(f"  {store}: 29.09 = {dates['2025-09-29']:.2f}, 30.09 = {dates['2025-09-30']:.2f}")
        
        return verification_cash
        
    except Exception as e:
        print(f"Ошибка загрузки эталонных данных: {e}")
        return None

def get_our_cash_data(start_date, end_date):
    """Получает наши данные по общей кассе"""
    try:
        with DatabaseConnector() as db:
            print(f"\n=== НАШИ ДАННЫЕ ПО ОБЩЕЙ КАССЕ ({start_date} - {end_date}) ===")
            
            # Получаем общую кассу по магазинам и датам
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
            
            sales = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей по общей кассе: {len(sales)}")
            
            if not sales.empty:
                print("\nНаши суммы по магазинам:")
                our_cash = {}
                for idx, row in sales.iterrows():
                    store = row['STORE_NAME']
                    date = row['SALE_DATE'].strftime('%Y-%m-%d')
                    total_cash = row['TOTAL_CASH']
                    
                    if store not in our_cash:
                        our_cash[store] = {}
                    our_cash[store][date] = total_cash
                    
                    print(f"  {store} | {date} | {total_cash:.2f}")
                
                return our_cash
            else:
                print("Нет данных по общей кассе за указанный период")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения данных по общей кассе: {e}")
        return None

def compare_cash_data(our_cash, verification_cash):
    """Сравнивает наши данные с эталонными"""
    print("\n=== СРАВНЕНИЕ СУММ ПРОДАЖ ===")
    
    if our_cash is None or verification_cash is None:
        print("Нет данных для сравнения")
        return
    
    print("\nСравнительная таблица сумм:")
    print("Магазин | Дата | Наша сумма | Эталон | Разница | Статус")
    print("-" * 70)
    
    total_our = 0
    total_ref = 0
    good_matches = 0
    total_matches = 0
    
    # Сравниваем по магазинам и датам
    for store in set(list(our_cash.keys()) + list(verification_cash.keys())):
        for date in ['2025-09-29', '2025-09-30']:
            our_amount = our_cash.get(store, {}).get(date, 0)
            ref_amount = verification_cash.get(store, {}).get(date, 0)
            
            if our_amount > 0 or ref_amount > 0:
                total_matches += 1
                
                diff = our_amount - ref_amount
                if abs(diff) < 1.0:
                    status = "ОТЛИЧНО"
                    good_matches += 1
                elif abs(diff) < 10.0:
                    status = "ХОРОШО"
                    good_matches += 1
                else:
                    status = "ПЛОХО"
                
                print(f"{store} | {date} | {our_amount:.2f} | {ref_amount:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_amount
                total_ref += ref_amount
    
    # Общая статистика
    print(f"\n=== ОБЩАЯ СТАТИСТИКА СУММ ===")
    total_diff = total_our - total_ref
    print(f"Общая наша сумма: {total_our:.2f} руб")
    print(f"Общая эталонная сумма: {total_ref:.2f} руб")
    print(f"Общая разница: {total_diff:+.2f} руб")
    print(f"Хороших совпадений: {good_matches}/{total_matches}")
    
    if abs(total_diff) < 10.0:
        print("ОТЛИЧНО! Суммы совпадают!")
    elif abs(total_diff) < 100.0:
        print("ХОРОШО! Суммы совпадают приемлемо")
    else:
        print("ПЛОХО! Есть расхождения в суммах")

def main():
    """Основная функция"""
    print("=== ПРОВЕРКА СУММ ПРОДАЖ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Загружаем эталонные данные
    print("\n" + "="*50)
    print("ЭТАП 1: Загрузка эталонных данных")
    print("="*50)
    
    verification_cash = load_verification_cash_data()
    
    # Этап 2: Получаем наши данные
    print("\n" + "="*50)
    print("ЭТАП 2: Получение наших данных")
    print("="*50)
    
    our_cash = get_our_cash_data("2025-09-29", "2025-09-30")
    
    # Этап 3: Сравниваем данные
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение данных")
    print("="*50)
    
    compare_cash_data(our_cash, verification_cash)
    
    print("\n" + "="*50)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("="*50)

if __name__ == "__main__":
    main()

