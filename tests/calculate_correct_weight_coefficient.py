#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расчет правильного коэффициента для перевода чашек в килограммы
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

def calculate_weight_coefficient():
    """Рассчитывает правильный коэффициент для перевода чашек в килограммы"""
    try:
        with DatabaseConnector() as db:
            print("=== РАСЧЕТ ПРАВИЛЬНОГО КОЭФФИЦИЕНТА ВЕСА ===")
            
            # Получаем данные по чашкам
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
            
            cups_data = db.execute_query(query, ("2025-09-29", "2025-09-30"))
            
            if cups_data.empty:
                print("Нет данных по чашкам")
                return None
            
            # Загружаем эталонные данные
            import pandas as pd
            excel_file = "data/данные для сверки.xlsx"
            kg_verification = pd.read_excel(excel_file, sheet_name="Количество килограмм")
            
            print("\nДанные по чашкам:")
            print(cups_data[['NAME', 'DAT_', 'ALLCUP']])
            
            print("\nЭталонные данные по килограммам:")
            print(kg_verification)
            
            # Рассчитываем коэффициент для каждого магазина и даты
            print("\n=== РАСЧЕТ КОЭФФИЦИЕНТОВ ===")
            coefficients = []
            
            for idx, row in cups_data.iterrows():
                store = row['NAME']
                date = row['DAT_'].strftime('%Y-%m-%d')
                cups = row['ALLCUP'] or 0
                
                # Ищем эталонные данные
                store_row = kg_verification[kg_verification['Unnamed: 0'] == store]
                if not store_row.empty:
                    if date == '2025-09-29':
                        ref_kg = store_row.iloc[0]['2025-09-29 00:00:00']
                    elif date == '2025-09-30':
                        ref_kg = store_row.iloc[0]['2025-09-30 00:00:00']
                    else:
                        ref_kg = 0
                    
                    if cups > 0 and ref_kg > 0:
                        coefficient = ref_kg / cups
                        coefficients.append(coefficient)
                        print(f"{store} ({date}): {cups} чашек -> {ref_kg} кг, коэффициент = {coefficient:.4f}")
                    else:
                        print(f"{store} ({date}): {cups} чашек -> {ref_kg} кг, пропускаем (нули)")
                else:
                    print(f"{store} ({date}): эталонные данные не найдены")
            
            if coefficients:
                avg_coefficient = sum(coefficients) / len(coefficients)
                min_coefficient = min(coefficients)
                max_coefficient = max(coefficients)
                
                print(f"\n=== РЕЗУЛЬТАТЫ ===")
                print(f"Количество расчетов: {len(coefficients)}")
                print(f"Средний коэффициент: {avg_coefficient:.4f} кг/чашка")
                print(f"Минимальный коэффициент: {min_coefficient:.4f} кг/чашка")
                print(f"Максимальный коэффициент: {max_coefficient:.4f} кг/чашка")
                
                # Тестируем разные коэффициенты
                print(f"\n=== ТЕСТИРОВАНИЕ КОЭФФИЦИЕНТОВ ===")
                test_coefficients = [0.01, 0.02, 0.03, 0.04, 0.05, avg_coefficient]
                
                for test_coef in test_coefficients:
                    print(f"\nКоэффициент {test_coef:.3f} кг/чашка:")
                    total_error = 0
                    count = 0
                    
                    for idx, row in cups_data.iterrows():
                        store = row['NAME']
                        date = row['DAT_'].strftime('%Y-%m-%d')
                        cups = row['ALLCUP'] or 0
                        calc_kg = cups * test_coef
                        
                        # Ищем эталонные данные
                        store_row = kg_verification[kg_verification['Unnamed: 0'] == store]
                        if not store_row.empty:
                            if date == '2025-09-29':
                                ref_kg = store_row.iloc[0]['2025-09-29 00:00:00']
                            elif date == '2025-09-30':
                                ref_kg = store_row.iloc[0]['2025-09-30 00:00:00']
                            else:
                                ref_kg = 0
                            
                            if ref_kg > 0:
                                error = abs(calc_kg - ref_kg)
                                total_error += error
                                count += 1
                                print(f"  {store} ({date}): {calc_kg:.2f} vs {ref_kg:.2f}, ошибка: {error:.2f}")
                    
                    if count > 0:
                        avg_error = total_error / count
                        print(f"  Средняя ошибка: {avg_error:.3f} кг")
                
                return avg_coefficient
            else:
                print("Не удалось рассчитать коэффициенты")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка расчета коэффициента: {e}")
        return None

def main():
    """Основная функция"""
    print("=== РАСЧЕТ ПРАВИЛЬНОГО КОЭФФИЦИЕНТА ВЕСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    coefficient = calculate_weight_coefficient()
    
    if coefficient:
        print(f"\n🎯 РЕКОМЕНДУЕМЫЙ КОЭФФИЦИЕНТ: {coefficient:.4f} кг/чашка")
        print(f"Это означает, что 1 чашка кофе весит примерно {coefficient*1000:.1f} грамм")
    else:
        print("❌ Не удалось рассчитать коэффициент")

if __name__ == "__main__":
    main()

