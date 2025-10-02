#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
АНАЛИЗ ЭТАЛОННЫХ ДАННЫХ
"""

import pandas as pd
import sys
import os
from datetime import datetime

def analyze_verification_data():
    """Анализирует эталонные данные из Excel файла"""
    try:
        print("=== АНАЛИЗ ЭТАЛОННЫХ ДАННЫХ ===")
        
        # Читаем Excel файл
        excel_file = "data/данные для сверки.xlsx"
        
        if not os.path.exists(excel_file):
            print(f"Файл {excel_file} не найден!")
            return None
        
        # Читаем вкладку "Общая касса"
        print("\n=== ВКЛАДКА 'ОБЩАЯ КАССА' ===")
        try:
            cash_data = pd.read_excel(excel_file, sheet_name="Общая касса")
            print("Структура данных 'Общая касса':")
            print(cash_data.head())
            print(f"Размер: {cash_data.shape}")
            print(f"Колонки: {list(cash_data.columns)}")
        except Exception as e:
            print(f"Ошибка чтения 'Общая касса': {e}")
        
        # Читаем вкладку "Количество килограмм"
        print("\n=== ВКЛАДКА 'КОЛИЧЕСТВО КИЛОГРАММ' ===")
        try:
            kg_data = pd.read_excel(excel_file, sheet_name="Количество килограмм")
            print("Структура данных 'Количество килограмм':")
            print(kg_data.head())
            print(f"Размер: {kg_data.shape}")
            print(f"Колонки: {list(kg_data.columns)}")
            
            # Анализируем данные по килограммам
            print("\nДетальный анализ килограммов:")
            for idx, row in kg_data.iterrows():
                print(f"Строка {idx}: {dict(row)}")
                
        except Exception as e:
            print(f"Ошибка чтения 'Количество килограмм': {e}")
        
        # Пробуем прочитать все вкладки
        print("\n=== ВСЕ ВКЛАДКИ В ФАЙЛЕ ===")
        try:
            excel_file_obj = pd.ExcelFile(excel_file)
            print(f"Вкладки в файле: {excel_file_obj.sheet_names}")
        except Exception as e:
            print(f"Ошибка чтения списка вкладок: {e}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка анализа эталонных данных: {e}")
        return None

def main():
    """Основная функция"""
    print("=== АНАЛИЗ ЭТАЛОННЫХ ДАННЫХ ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyze_verification_data()
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()