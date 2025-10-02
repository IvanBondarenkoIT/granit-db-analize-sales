#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой расчет правильного коэффициента для перевода чашек в килограммы
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

def calculate_simple_coefficient():
    """Простой расчет коэффициента"""
    try:
        # Данные из предыдущего анализа
        cups_data = [
            ("CityMall", "2025-09-29", 28.0, 1.25),
            ("CityMall", "2025-09-30", 23.0, 0.50),
            ("DK Batumi", "2025-09-29", 48.0, 4.25),
            ("DK Batumi", "2025-09-30", 22.0, 3.25),
            ("DK Paliashvili", "2025-09-29", 11.0, 0.75),
            ("DK Paliashvili", "2025-09-30", 9.0, 0.50),
            ("EastPoint", "2025-09-29", 73.0, 0.25),
            ("EastPoint", "2025-09-30", 113.0, 5.25)
        ]
        
        print("=== РАСЧЕТ КОЭФФИЦИЕНТОВ ===")
        coefficients = []
        
        for store, date, cups, ref_kg in cups_data:
            if cups > 0 and ref_kg > 0:
                coefficient = ref_kg / cups
                coefficients.append(coefficient)
                print(f"{store} ({date}): {cups} чашек -> {ref_kg} кг, коэффициент = {coefficient:.4f}")
        
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
            
            best_coefficient = None
            best_error = float('inf')
            
            for test_coef in test_coefficients:
                print(f"\nКоэффициент {test_coef:.3f} кг/чашка:")
                total_error = 0
                count = 0
                
                for store, date, cups, ref_kg in cups_data:
                    if ref_kg > 0:
                        calc_kg = cups * test_coef
                        error = abs(calc_kg - ref_kg)
                        total_error += error
                        count += 1
                        print(f"  {store} ({date}): {calc_kg:.2f} vs {ref_kg:.2f}, ошибка: {error:.2f}")
                
                if count > 0:
                    avg_error = total_error / count
                    print(f"  Средняя ошибка: {avg_error:.3f} кг")
                    
                    if avg_error < best_error:
                        best_error = avg_error
                        best_coefficient = test_coef
            
            print(f"\n=== ЛУЧШИЙ КОЭФФИЦИЕНТ ===")
            print(f"Коэффициент: {best_coefficient:.4f} кг/чашка")
            print(f"Средняя ошибка: {best_error:.3f} кг")
            print(f"Это означает, что 1 чашка кофе весит примерно {best_coefficient*1000:.1f} грамм")
            
            return best_coefficient
        else:
            print("Не удалось рассчитать коэффициенты")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка расчета коэффициента: {e}")
        return None

def test_final_calculation(coefficient):
    """Тестирует финальный расчет с найденным коэффициентом"""
    if not coefficient:
        return
    
    print(f"\n=== ФИНАЛЬНЫЙ ТЕСТ С КОЭФФИЦИЕНТОМ {coefficient:.4f} ===")
    
    cups_data = [
        ("CityMall", "2025-09-29", 28.0, 1.25),
        ("CityMall", "2025-09-30", 23.0, 0.50),
        ("DK Batumi", "2025-09-29", 48.0, 4.25),
        ("DK Batumi", "2025-09-30", 22.0, 3.25),
        ("DK Paliashvili", "2025-09-29", 11.0, 0.75),
        ("DK Paliashvili", "2025-09-30", 9.0, 0.50),
        ("EastPoint", "2025-09-29", 73.0, 0.25),
        ("EastPoint", "2025-09-30", 113.0, 5.25)
    ]
    
    print("Магазин | Дата | Чашки | Наш расчет | Эталон | Ошибка | Статус")
    print("-" * 70)
    
    total_error = 0
    count = 0
    
    for store, date, cups, ref_kg in cups_data:
        if ref_kg > 0:
            calc_kg = cups * coefficient
            error = abs(calc_kg - ref_kg)
            total_error += error
            count += 1
            
            if error < 0.1:
                status = "OK"
            elif error < 0.5:
                status = "ХОРОШО"
            else:
                status = "ПЛОХО"
            
            print(f"{store} | {date} | {cups} | {calc_kg:.2f} | {ref_kg:.2f} | {error:.2f} | {status}")
    
    if count > 0:
        avg_error = total_error / count
        print(f"\nСредняя ошибка: {avg_error:.3f} кг")
        
        if avg_error < 0.2:
            print("ОТЛИЧНО! Коэффициент работает хорошо")
        elif avg_error < 0.5:
            print("ХОРОШО! Коэффициент работает приемлемо")
        else:
            print("ПЛОХО! Нужен другой подход")

def main():
    """Основная функция"""
    print("=== ПРОСТОЙ РАСЧЕТ КОЭФФИЦИЕНТА ВЕСА ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    coefficient = calculate_simple_coefficient()
    
    if coefficient:
        test_final_calculation(coefficient)
    else:
        print("Не удалось рассчитать коэффициент")

if __name__ == "__main__":
    main()

