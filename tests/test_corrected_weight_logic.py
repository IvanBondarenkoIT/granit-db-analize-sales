#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование исправленной логики расчета веса
Коэффициент 0.05 кг за чашку
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

def test_corrected_weight_logic():
    """Тестирует исправленную логику расчета веса"""
    try:
        with DatabaseConnector() as db:
            print("=== ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ ЛОГИКИ РАСЧЕТА ВЕСА ===")
            
            # Используем оригинальный запрос
            query = """
            SELECT 
                stgp.name as STORE_NAME,
                D.DAT_ as SALE_DATE,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789') THEN GD.Source ELSE NULL END) AS MonoCup,
                SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') THEN GD.Source ELSE NULL END) AS BlendCup,
                SUM(CASE WHEN G.OWNER IN ('24491','21385') THEN GD.Source ELSE NULL END) AS CaotinaCup,
                SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789','23076','21882','25767','248882','25788','24491','21385') THEN GD.Source ELSE NULL END) AS AllCup
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
                
                # Рассчитываем вес по исправленной логике: все чашки * 0.05 кг
                result['TOTAL_WEIGHT_KG'] = result['ALLCUP'] * 0.05
                
                print("\nРасчет веса (все чашки * 0.05 кг):")
                print(result[['STORE_NAME', 'SALE_DATE', 'ALLCUP', 'TOTAL_WEIGHT_KG']])
                
                return result
            else:
                print("Нет данных")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка тестирования логики: {e}")
        return None

def compare_with_verification_corrected(coffee_data):
    """Сравнивает исправленную логику с эталонными данными"""
    print("\n=== СРАВНЕНИЕ ИСПРАВЛЕННОЙ ЛОГИКИ С ЭТАЛОННЫМИ ДАННЫМИ ===")
    
    # Эталонные данные
    verification_data = {
        'CityMall': {'2025-09-29': 1.25, '2025-09-30': 0.50},
        'DK Batumi': {'2025-09-29': 4.25, '2025-09-30': 3.25},
        'DK Paliashvili': {'2025-09-29': 0.75, '2025-09-30': 0.50},
        'EastPoint': {'2025-09-29': 0.25, '2025-09-30': 5.25}
    }
    
    if coffee_data is not None and not coffee_data.empty:
        print("\nСравнительная таблица:")
        print("Магазин | Дата | Чашки | Наш расчет | Эталон | Разница | Статус")
        print("-" * 80)
        
        total_our = 0
        total_ref = 0
        good_matches = 0
        total_matches = 0
        
        for idx, row in coffee_data.iterrows():
            store = row['STORE_NAME']
            date = row['SALE_DATE'].strftime('%Y-%m-%d')
            cups = row['ALLCUP'] or 0
            our_weight = row['TOTAL_WEIGHT_KG'] or 0
            
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
                
                print(f"{store} | {date} | {cups} | {our_weight:.2f} | {ref_weight:.2f} | {diff:+.2f} | {status}")
                
                total_our += our_weight
                total_ref += ref_weight
            else:
                print(f"{store} | {date} | {cups} | {our_weight:.2f} | НЕТ ДАННЫХ | - | -")
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
        
        # Анализ по магазинам
        print(f"\n=== АНАЛИЗ ПО МАГАЗИНАМ ===")
        for store in verification_data.keys():
            store_data = coffee_data[coffee_data['STORE_NAME'] == store]
            if not store_data.empty:
                store_our = store_data['TOTAL_WEIGHT_KG'].sum()
                store_ref = sum(verification_data[store].values())
                store_diff = store_our - store_ref
                print(f"{store}: {store_our:.2f} vs {store_ref:.2f} (разница: {store_diff:+.2f})")

def main():
    """Основная функция"""
    print("=== ТЕСТИРОВАНИЕ ИСПРАВЛЕННОЙ ЛОГИКИ РАСЧЕТА ВЕСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Тестируем исправленную логику
    print("\n" + "="*50)
    print("ЭТАП 1: Тестирование логики (все чашки * 0.05 кг)")
    print("="*50)
    
    coffee_data = test_corrected_weight_logic()
    
    # Этап 2: Сравниваем с эталонными данными
    print("\n" + "="*50)
    print("ЭТАП 2: Сравнение с эталонными данными")
    print("="*50)
    
    compare_with_verification_corrected(coffee_data)
    
    print("\n" + "="*50)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*50)

if __name__ == "__main__":
    main()

