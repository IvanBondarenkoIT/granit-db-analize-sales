"""
Скрипт для тестирования подключения к удаленной БД Firebird.

Выполняет безопасные тесты:
1. Проверка подключения
2. Получение информации о БД
3. Тестовые запросы
4. Проверка блокировки опасных операций
"""

import sys
import os
from pathlib import Path

# Добавить корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.remote_db_connector import RemoteDatabaseConnector
from src.logger_config import setup_logger


def print_section(title: str):
    """Красивый вывод заголовка секции."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_basic_connection(connector: RemoteDatabaseConnector):
    """Тест 1: Базовое подключение."""
    print_section("ТЕСТ 1: Проверка подключения к удаленной БД")
    
    success, message = connector.test_connection()
    print(f"Результат: {message}")
    
    if not success:
        print("ОШИБКА: Не удалось подключиться к БД!")
        print("Проверьте:")
        print("  1. Доступность сервера (ping 85.114.224.45)")
        print("  2. Открыт ли порт 3050 на сервере")
        print("  3. Правильность пути к БД")
        print("  4. Учетные данные")
        return False
    
    return True


def test_database_info(connector: RemoteDatabaseConnector):
    """Тест 2: Получение информации о БД."""
    print_section("ТЕСТ 2: Информация о базе данных")
    
    try:
        db_info = connector.get_database_info()
        
        print("Информация о БД:")
        print(f"  Хост: {db_info.get('host')}")
        print(f"  Порт: {db_info.get('port')}")
        print(f"  База данных: {db_info.get('database')}")
        print(f"  Пользователь: {db_info.get('user')}")
        print(f"  Режим READ-ONLY: {db_info.get('read_only')}")
        print(f"  Подключено: {db_info.get('connected')}")
        
        if db_info.get('connected'):
            print(f"  Версия Firebird: {db_info.get('firebird_version')}")
            print(f"  Количество таблиц: {db_info.get('tables_count')}")
        
        if 'error' in db_info:
            print(f"  ОШИБКА: {db_info.get('error')}")
            return False
        
        print("\nТест пройден успешно!")
        return True
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def test_simple_query(connector: RemoteDatabaseConnector):
    """Тест 3: Простой SELECT запрос."""
    print_section("ТЕСТ 3: Выполнение простого SELECT запроса")
    
    try:
        query = "SELECT 1 AS TEST_VALUE FROM RDB$DATABASE"
        print(f"Запрос: {query}")
        
        df = connector.execute_query_to_dataframe(query)
        print(f"\nРезультат:")
        print(df)
        
        print("\nТест пройден успешно!")
        return True
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def test_stores_query(connector: RemoteDatabaseConnector):
    """Тест 4: Запрос списка магазинов."""
    print_section("ТЕСТ 4: Получение списка магазинов")
    
    try:
        query = """
        SELECT FIRST 10 
            ID, 
            NAME 
        FROM STORGRP 
        ORDER BY NAME
        """
        print("Запрос: SELECT первых 10 магазинов")
        
        df = connector.execute_query_to_dataframe(query)
        print(f"\nНайдено магазинов: {len(df)}")
        print("\nПервые магазины:")
        print(df.to_string(index=False))
        
        print("\nТест пройден успешно!")
        return True
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def test_sales_data_query(connector: RemoteDatabaseConnector):
    """Тест 5: Запрос данных о продажах."""
    print_section("ТЕСТ 5: Получение данных о продажах (последние 5 записей)")
    
    try:
        query = """
        SELECT FIRST 5
            D.ID,
            D.DAT_ as ORDER_DATE,
            stgp.NAME as STORE_NAME,
            D.ALLCUP as CUPS
        FROM STORZAKAZDT D
        JOIN STORGRP stgp ON D.STORGRPID = stgp.ID
        WHERE D.DAT_ >= '2025-09-01'
        ORDER BY D.DAT_ DESC
        """
        print("Запрос: Последние 5 заказов с сентября 2025")
        
        df = connector.execute_query_to_dataframe(query)
        print(f"\nНайдено записей: {len(df)}")
        
        if len(df) > 0:
            print("\nДанные:")
            print(df.to_string(index=False))
        else:
            print("\nДанных за указанный период не найдено")
        
        print("\nТест пройден успешно!")
        return True
        
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return False


def test_forbidden_operations(connector: RemoteDatabaseConnector):
    """Тест 6: Проверка блокировки опасных операций."""
    print_section("ТЕСТ 6: Проверка блокировки опасных операций (БЕЗОПАСНОСТЬ)")
    
    dangerous_queries = [
        ("UPDATE", "UPDATE STORGRP SET NAME = 'Test' WHERE ID = 1"),
        ("DELETE", "DELETE FROM STORGRP WHERE ID = 1"),
        ("INSERT", "INSERT INTO STORGRP (NAME) VALUES ('Test')"),
        ("DROP", "DROP TABLE STORGRP"),
        ("ALTER", "ALTER TABLE STORGRP ADD COLUMN TEST VARCHAR(50)"),
        ("TRUNCATE", "TRUNCATE TABLE STORGRP"),
    ]
    
    all_blocked = True
    
    for operation, query in dangerous_queries:
        print(f"\nПопытка выполнить {operation}...")
        print(f"  Запрос: {query[:60]}...")
        
        try:
            connector.execute_query(query)
            print(f"  ОШИБКА: {operation} НЕ БЫЛ ЗАБЛОКИРОВАН!")
            all_blocked = False
        except ValueError as e:
            print(f"  OK: Запрос заблокирован системой безопасности")
        except Exception as e:
            print(f"  OK: Запрос заблокирован ({type(e).__name__})")
    
    if all_blocked:
        print("\nВсе опасные операции успешно заблокированы!")
        print("Тест пройден успешно!")
        return True
    else:
        print("\nВНИМАНИЕ: Некоторые опасные операции НЕ были заблокированы!")
        return False


def main():
    """Главная функция тестирования."""
    logger = setup_logger()
    
    print("\n" + "=" * 80)
    print("  ТЕСТИРОВАНИЕ БЕЗОПАСНОГО ПОДКЛЮЧЕНИЯ К УДАЛЕННОЙ БД")
    print("  Рабочая база: G:\\Гранит\\GRANITDB\\GEORGIA.GDB")
    print("  Режим: READ-ONLY (только чтение)")
    print("=" * 80)
    
    # Создание коннектора
    print("\nИнициализация коннектора...")
    try:
        connector = RemoteDatabaseConnector()
        print("OK: Коннектор создан")
    except Exception as e:
        print(f"ОШИБКА при создании коннектора: {e}")
        return 1
    
    # Список тестов
    tests = [
        ("Базовое подключение", test_basic_connection),
        ("Информация о БД", test_database_info),
        ("Простой запрос", test_simple_query),
        ("Список магазинов", test_stores_query),
        ("Данные о продажах", test_sales_data_query),
        ("Блокировка опасных операций", test_forbidden_operations),
    ]
    
    # Выполнение тестов
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(connector)
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоговые результаты
    print_section("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Пройдено тестов: {passed}/{total}\n")
    
    for test_name, result in results:
        status = "OK" if result else "FAIL"
        emoji = "✅" if result else "❌"
        print(f"{emoji} {status:6} | {test_name}")
    
    print("\n" + "=" * 80)
    
    if passed == total:
        print("\nПОЗДРАВЛЯЮ! Все тесты пройдены успешно!")
        print("Удаленное подключение работает корректно и безопасно.")
        return 0
    else:
        print(f"\nВНИМАНИЕ! Не пройдено тестов: {total - passed}")
        print("Проверьте логи для деталей.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

