#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа структуры таблицы STORZDTGDS
Находим правильные поля для суммы и количества товаров
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

def analyze_storzdtgds_structure():
    """Анализирует структуру таблицы STORZDTGDS"""
    try:
        with DatabaseConnector() as db:
            print("=== АНАЛИЗ СТРУКТУРЫ ТАБЛИЦЫ STORZDTGDS ===")
            
            # Получаем информацию о полях таблицы
            query = """
            SELECT 
                RDB$FIELD_NAME as FIELD_NAME,
                RDB$FIELD_TYPE as FIELD_TYPE,
                RDB$FIELD_LENGTH as FIELD_LENGTH,
                RDB$FIELD_SCALE as FIELD_SCALE
            FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'STORZDTGDS'
            ORDER BY RDB$FIELD_POSITION
            """
            
            fields = db.execute_query(query)
            print(f"Найдено полей в таблице STORZDTGDS: {len(fields)}")
            
            if not fields.empty:
                print("\nПоля таблицы STORZDTGDS:")
                for idx, row in fields.iterrows():
                    field_name = row['FIELD_NAME'].strip()
                    field_type = row['FIELD_TYPE']
                    field_length = row['FIELD_LENGTH']
                    field_scale = row['FIELD_SCALE']
                    
                    print(f"  {field_name}: тип={field_type}, длина={field_length}, масштаб={field_scale}")
                
                return fields
            else:
                print("Не удалось получить информацию о полях таблицы")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка анализа структуры таблицы: {e}")
        return None

def get_sample_data_from_storzdtgds():
    """Получает образцы данных из таблицы STORZDTGDS"""
    try:
        with DatabaseConnector() as db:
            print("\n=== ОБРАЗЦЫ ДАННЫХ ИЗ STORZDTGDS ===")
            
            # Получаем первые 10 записей
            query = """
            SELECT FIRST 10 *
            FROM STORZDTGDS
            """
            
            sample_data = db.execute_query(query)
            print(f"Получено образцов данных: {len(sample_data)}")
            
            if not sample_data.empty:
                print("\nОбразцы данных:")
                print(sample_data)
                return sample_data
            else:
                print("Нет данных в таблице STORZDTGDS")
                return None
                
    except Exception as e:
        logger.error(f"Ошибка получения образцов данных: {e}")
        return None

def test_coffee_sales_query():
    """Тестирует запрос для получения продаж кофе с правильными полями"""
    try:
        with DatabaseConnector() as db:
            print("\n=== ТЕСТ ЗАПРОСА ПРОДАЖ КОФЕ ===")
            
            # Тестируем запрос с разными полями для суммы
            test_queries = [
                {
                    "name": "С полем SOURCE (количество)",
                    "query": """
                    SELECT 
                        stgp.name as STORE_NAME,
                        D.DAT_ as SALE_DATE,
                        G.NAME as PRODUCT_NAME,
                        GD.SOURCE as QUANTITY,
                        GD.SOURCE * 0.25 as ESTIMATED_WEIGHT,
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
                    ORDER BY stgp.name, D.DAT_, G.NAME
                    """
                },
                {
                    "name": "С полем SUMMA (если существует)",
                    "query": """
                    SELECT 
                        stgp.name as STORE_NAME,
                        D.DAT_ as SALE_DATE,
                        G.NAME as PRODUCT_NAME,
                        GD.SOURCE as QUANTITY,
                        GD.SUMMA as ITEM_SUM,
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
                    ORDER BY stgp.name, D.DAT_, G.NAME
                    """
                }
            ]
            
            for test in test_queries:
                print(f"\n--- {test['name']} ---")
                try:
                    result = db.execute_query(test['query'], ("2025-09-29", "2025-09-30"))
                    if not result.empty:
                        print(f"✅ Успешно! Получено записей: {len(result)}")
                        print("Первые 3 записи:")
                        print(result.head(3))
                    else:
                        print("❌ Нет данных")
                except Exception as e:
                    print(f"❌ Ошибка: {e}")
                    
    except Exception as e:
        logger.error(f"Ошибка тестирования запросов: {e}")
        return None

def main():
    """Основная функция для анализа структуры таблицы"""
    print("=== АНАЛИЗ СТРУКТУРЫ ТАБЛИЦЫ STORZDTGDS ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 1: Анализируем структуру таблицы
    print("\n" + "="*50)
    print("ЭТАП 1: Анализ структуры таблицы STORZDTGDS")
    print("="*50)
    
    fields = analyze_storzdtgds_structure()
    
    # Этап 2: Получаем образцы данных
    print("\n" + "="*50)
    print("ЭТАП 2: Образцы данных из STORZDTGDS")
    print("="*50)
    
    sample_data = get_sample_data_from_storzdtgds()
    
    # Этап 3: Тестируем запросы
    print("\n" + "="*50)
    print("ЭТАП 3: Тестирование запросов продаж кофе")
    print("="*50)
    
    test_coffee_sales_query()
    
    print("\n" + "="*50)
    print("АНАЛИЗ ЗАВЕРШЕН")
    print("="*50)

if __name__ == "__main__":
    main()

