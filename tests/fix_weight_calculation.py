#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленный расчет килограммов
Используем только товары с весом в названии
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

def get_corrected_weight_calculation(start_date, end_date):
    """Получает исправленный расчет килограммов"""
    try:
        with DatabaseConnector() as db:
            print(f"=== ИСПРАВЛЕННЫЙ РАСЧЕТ КИЛОГРАММОВ ({start_date} - {end_date}) ===")
            
            # Запрос только для товаров с весом в названии
            query = """
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
                AND G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385')
                AND (G.NAME LIKE '%кг%' OR G.NAME LIKE '%kg%' OR G.NAME LIKE '%г%' OR G.NAME LIKE '%g%')
            ORDER BY stgp.name, D.DAT_, G.NAME
            """
            
            data = db.execute_query(query, (start_date, end_date))
            print(f"Получено записей с весом в названии: {len(data)}")
            
            if data.empty:
                print("Нет товаров с весом в названии")
                return None
            
            print("\nТовары с весом в названии:")
            for idx, row in data.iterrows():
                print(f"  {row['PRODUCT_NAME']} - {row['QUANTITY']} шт")
            
            # Рассчитываем вес
            data['ITEM_WEIGHT'] = data['PRODUCT_NAME'].apply(extract_weight_from_name)
            data['TOTAL_WEIGHT'] = data['QUANTITY'] * data['ITEM_WEIGHT']
            
            print("\nРасчет веса по товарам:")
            for idx, row in data.iterrows():
                print(f"  {row['PRODUCT_NAME']}")
                print(f"    Количество: {row['QUANTITY']}")
                print(f"    Вес за единицу: {row['ITEM_WEIGHT']} кг")
                print(f"    Общий вес: {row['TOTAL_WEIGHT']} кг")
                print()
            
            # Группируем по магазинам и датам
            grouped = data.groupby(['STORE_NAME', 'SALE_DATE']).agg({
                'QUANTITY': 'sum',
                'TOTAL_WEIGHT': 'sum'
            }).reset_index()
            
            print("Итоговые килограммы по магазинам:")
            print(grouped)
            
            return grouped
            
    except Exception as e:
        logger.error(f"Ошибка исправленного расчета веса: {e}")
        return None

def extract_weight_from_name(product_name):
    """Извлекает вес из названия товара"""
    import re
    
    if not product_name:
        return 0.0
    
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
    
    return 0.0

def load_verification_data():
    """Загружает эталонные данные"""
    try:
        import pandas as pd
        excel_file = "data/данные для сверки.xlsx"
        kg_data = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        print("\n=== ЭТАЛОННЫЕ ДАННЫЕ ===")
        print(kg_data)
        return kg_data
    except Exception as e:
        logger.error(f"Ошибка загрузки эталонных данных: {e}")
        return None

def compare_with_verification(our_data, verification_data):
    """Сравнивает с эталонными данными"""
    print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
    if our_data is None or our_data.empty:
        print("Нет наших данных для сравнения")
        return
    
    print("Наши данные (исправленные):")
    print(our_data)
    
    if verification_data is not None:
        print("\nЭталонные данные:")
        print(verification_data)
        
        # Создаем сравнительную таблицу
        print("\nСравнительная таблица:")
        print("Магазин | Дата | Наши данные | Эталон | Разница")
        print("-" * 50)
        
        for idx, row in our_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            our_weight = row['TOTAL_WEIGHT']
            
            # Ищем соответствующие эталонные данные
            if verification_data is not None and not verification_data.empty:
                # Преобразуем даты в эталонных данных
                verification_data_copy = verification_data.copy()
                verification_data_copy.columns = ['Store', 'Date1', 'Date2']
                
                # Ищем магазин
                store_row = verification_data_copy[verification_data_copy['Store'] == store]
                if not store_row.empty:
                    if date == '2025-09-29':
                        ref_weight = store_row['Date1'].iloc[0]
                    elif date == '2025-09-30':
                        ref_weight = store_row['Date2'].iloc[0]
                    else:
                        ref_weight = 0
                    
                    diff = our_weight - ref_weight
                    status = "✅" if abs(diff) < 0.1 else "❌"
                    
                    print(f"{store} | {date} | {our_weight:.2f} кг | {ref_weight:.2f} кг | {diff:+.2f} кг {status}")
                else:
                    print(f"{store} | {date} | {our_weight:.2f} кг | НЕТ ДАННЫХ | - {status}")

def main():
    """Основная функция"""
    print("=== ИСПРАВЛЕННЫЙ РАСЧЕТ КИЛОГРАММОВ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Получаем исправленные данные
    print("\n" + "="*50)
    print("ЭТАП 1: Получение исправленных данных")
    print("="*50)
    
    corrected_data = get_corrected_weight_calculation("2025-09-29", "2025-09-30")
    
    # Этап 2: Загружаем эталонные данные
    print("\n" + "="*50)
    print("ЭТАП 2: Загрузка эталонных данных")
    print("="*50)
    
    verification_data = load_verification_data()
    
    # Этап 3: Сравниваем данные
    print("\n" + "="*50)
    print("ЭТАП 3: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification(corrected_data, verification_data)
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

