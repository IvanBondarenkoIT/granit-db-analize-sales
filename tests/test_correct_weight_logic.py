#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование правильной логики расчета веса
Все товары кофе * 0.25 кг за единицу
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

def test_correct_weight_logic():
    """Тестирует правильную логику расчета веса"""
    try:
        with DatabaseConnector() as db:
            print("=== ТЕСТИРОВАНИЕ ПРАВИЛЬНОЙ ЛОГИКИ РАСЧЕТА ВЕСА ===")
            
            # Используем оригинальный запрос для получения всех товаров кофе
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789') THEN GD.Source ELSE NULL END) AS MonoCup,
                SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') THEN GD.Source ELSE NULL END) AS BlendCup,
                SUM(CASE WHEN G.OWNER IN ('24491','21385') THEN GD.Source ELSE NULL END) AS CaotinaCup,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385') THEN GD.Source ELSE NULL END) AS AllCup,
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
            
            result = db.execute_query(query, ("2025-09-29", "2025-09-30"))
            print(f"Получено записей: {len(result)}")
            
            if not result.empty:
                print("\nДанные по чашкам:")
                print(result)
                
                # Рассчитываем вес по правильной логике: все чашки * 0.25 кг
                result['TOTAL_WEIGHT_KG'] = result['ALLCUP'] * 0.25
                
                print("\nРасчет веса (все чашки * 0.25 кг):")
                print(result[['STORE_NAME', 'DAT_', 'ALLCUP', 'TOTAL_WEIGHT_KG']])
                
                return result
            else:
                print("Нет данных")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования логики: {e}")
        return None

def compare_with_verification_data(coffee_data):
    """Сравнивает с эталонными данными"""
    try:
        import pandas as pd
        
        print("\n=== СРАВНЕНИЕ С ЭТАЛОННЫМИ ДАННЫМИ ===")
        
        # Загружаем эталонные данные
        excel_file = "data/данные для сверки.xlsx"
        kg_verification = pd.read_excel(excel_file, sheet_name="Количество килограмм")
        
        print("Эталонные данные по килограммам:")
        print(kg_verification)
        
        if coffee_data is not None and not coffee_data.empty:
            print("\nНаши данные (все чашки * 0.25 кг):")
            print(coffee_data[['STORE_NAME', 'DAT_', 'ALLCUP', 'TOTAL_WEIGHT_KG']])
            
            print("\nСравнительная таблица:")
            print("Магазин | Дата | Чашки | Наш расчет | Эталон | Разница | Статус")
            print("-" * 80)
            
            for idx, row in coffee_data.iterrows():
                store = row['STORE_NAME']
                date = row['DAT_'].strftime('%Y-%m-%d')
                cups = row['ALLCUP'] or 0
                our_weight = row['TOTAL_WEIGHT_KG'] or 0
                
                # Ищем эталонные данные
                store_row = kg_verification[kg_verification['Unnamed: 0'] == store]
                if not store_row.empty:
                    if date == '2025-09-29':
                        ref_weight = store_row.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_weight = store_row.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_weight = 0
                    
                    diff = our_weight - ref_weight
                    if abs(diff) < 0.1:
                        status = "OK"
                    elif abs(diff) < 0.5:
                        status = "ХОРОШО"
                    else:
                        status = "ПЛОХО"
                    
                    print(f"{store} | {date} | {cups} | {our_weight:.2f} | {ref_weight:.2f} | {diff:+.2f} | {status}")
                else:
                    print(f"{store} | {date} | {cups} | {our_weight:.2f} | НЕТ ДАННЫХ | - | -")
            
            # Рассчитываем общую статистику
            print(f"\n=== ОБЩАЯ СТАТИСТИКА ===")
            total_our = coffee_data['TOTAL_WEIGHT_KG'].sum()
            total_ref = 0
            
            for idx, row in coffee_data.iterrows():
                store = row['STORE_NAME']
                date = row['DAT_'].strftime('%Y-%m-%d')
                store_row = kg_verification[kg_verification['Unnamed: 0'] == store]
                if not store_row.empty:
                    if date == '2025-09-29':
                        ref_weight = store_row.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_weight = store_row.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_weight = 0
                    total_ref += ref_weight
            
            total_diff = total_our - total_ref
            print(f"Общий наш расчет: {total_our:.2f} кг")
            print(f"Общий эталон: {total_ref:.2f} кг")
            print(f"Общая разница: {total_diff:+.2f} кг")
            
            if abs(total_diff) < 1.0:
                print("ОТЛИЧНО! Логика работает правильно!")
            elif abs(total_diff) < 2.0:
                print("ХОРОШО! Логика работает приемлемо")
            else:
                print("ПЛОХО! Нужна корректировка логики")
        
    except Exception as e:
        logger.error(f"Ошибка сравнения с эталонными данными: {e}")

def main():
    """Основная функция"""
    print("=== ТЕСТИРОВАНИЕ ПРАВИЛЬНОЙ ЛОГИКИ РАСЧЕТА ВЕСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Тестируем правильную логику
    print("\n" + "="*50)
    print("ЭТАП 1: Тестирование логики (все чашки * 0.25 кг)")
    print("="*50)
    
    coffee_data = test_correct_weight_logic()
    
    # Этап 2: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 2: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_data(coffee_data)
    
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*50)

if __name__ == "__main__":
    main()

