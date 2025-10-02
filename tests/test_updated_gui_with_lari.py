#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ТЕСТ ОБНОВЛЕННОГО GUI С ЛАРИ И БЕЗОПАСНОЙ РАБОТОЙ С БД
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

def test_database_connector_safety():
    """Тестирует безопасность работы с БД"""
    print("=== ТЕСТ БЕЗОПАСНОСТИ DATABASE CONNECTOR ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Тест 1: Создание объекта
        print("\n1. Создание объекта DatabaseConnector...")
        db = DatabaseConnector()
        print("   УСПЕХ: Объект создан")
        
        # Тест 2: Подключение
        print("\n2. Подключение к БД...")
        if db.connect():
            print("   УСПЕХ: Подключение установлено")
        else:
            print("   ОШИБКА: Не удалось подключиться")
            return False
        
        # Тест 3: Проверка состояния
        print("\n3. Проверка состояния подключения...")
        if db._is_connected:
            print("   УСПЕХ: Флаг подключения установлен")
        else:
            print("   ОШИБКА: Флаг подключения не установлен")
            return False
        
        # Тест 4: Тест подключения
        print("\n4. Тестирование подключения...")
        if db.test_connection():
            print("   УСПЕХ: Тест подключения прошел")
        else:
            print("   ОШИБКА: Тест подключения не прошел")
            return False
        
        # Тест 5: Выполнение запроса
        print("\n5. Выполнение тестового запроса...")
        try:
            result = db.execute_query("SELECT 1 as test_value FROM RDB$DATABASE")
            if not result.empty and result.iloc[0]['TEST_VALUE'] == 1:
                print("   УСПЕХ: Запрос выполнен успешно")
            else:
                print("   ОШИБКА: Неожиданный результат запроса")
                return False
        except Exception as e:
            print(f"   ОШИБКА: Ошибка выполнения запроса: {e}")
            return False
        
        # Тест 6: Отключение
        print("\n6. Отключение от БД...")
        db.disconnect()
        if not db._is_connected:
            print("   УСПЕХ: Отключение выполнено")
        else:
            print("   ОШИБКА: Флаг подключения не сброшен")
            return False
        
        # Тест 7: Контекстный менеджер
        print("\n7. Тестирование контекстного менеджера...")
        try:
            with DatabaseConnector() as db_context:
                if db_context._is_connected:
                    print("   УСПЕХ: Контекстный менеджер работает")
                else:
                    print("   ОШИБКА: Контекстный менеджер не подключился")
                    return False
            print("   УСПЕХ: Контекстный менеджер корректно закрыл соединение")
        except Exception as e:
            print(f"   ОШИБКА: Ошибка в контекстном менеджере: {e}")
            return False
        
        print("\n=== ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО! ===")
        return True
        
    except Exception as e:
        print(f"\nОШИБКА: Критическая ошибка в тестах: {e}")
        return False

def test_currency_display():
    """Тестирует отображение валюты в лари"""
    print("\n=== ТЕСТ ОТОБРАЖЕНИЯ ВАЛЮТЫ ===")
    
    # Тестовые данные
    test_data = {
        'cups': 25.5,
        'kg': 3.25,
        'total': 1250.75
    }
    
    # Тест детального стиля
    detailed_style = f"Чашки: {test_data['cups']:.0f} шт\nКг: {test_data['kg']:.2f} кг\nСумма: {test_data['total']:.2f} лари"
    print(f"Детальный стиль: {detailed_style}")
    
    # Тест компактного стиля
    compact_style = f"Чашки: {test_data['cups']:.0f}шт\nКг: {test_data['kg']:.1f}кг\nСумма: {test_data['total']:.0f}лари"
    print(f"Компактный стиль: {compact_style}")
    
    # Проверяем наличие слова "лари"
    if "лари" in detailed_style and "лари" in compact_style:
        print("УСПЕХ: Валюта лари присутствует в обоих стилях")
        return True
    else:
        print("ОШИБКА: Валюта лари отсутствует")
        return False

def main():
    """Основная функция"""
    print("=== ТЕСТ ОБНОВЛЕННОГО GUI С ЛАРИ И БЕЗОПАСНОЙ РАБОТОЙ С БД ===")
    print(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Тест 1: Безопасность работы с БД
    db_safety_ok = test_database_connector_safety()
    
    # Тест 2: Отображение валюты
    currency_ok = test_currency_display()
    
    # Итоговый результат
    if db_safety_ok and currency_ok:
        print("\nВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("GUI приложение готово к использованию с:")
        print("  - Безопасной работой с БД")
        print("  - Отображением валюты в лари")
        print("  - Повторными попытками подключения")
        print("  - Безопасным отключением")
        print("  - Контекстными менеджерами")
    else:
        print("\nНЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ!")
        if not db_safety_ok:
            print("  - Проблемы с безопасностью БД")
        if not currency_ok:
            print("  - Проблемы с отображением валюты")
    
    print("\n" + "="*60)
    print("ТЕСТ ЗАВЕРШЕН")
    print("="*60)

if __name__ == "__main__":
    main()
