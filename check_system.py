#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - System Check

Проверка системы и зависимостей.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Проверка версии Python."""
    print("Проверка версии Python...")
    
    if sys.version_info < (3, 8):
        print(f"ОШИБКА: Требуется Python 3.8 или выше! Текущая версия: {sys.version_info.major}.{sys.version_info.minor}")
        return False
    else:
        print(f"OK: Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True

def check_virtual_environment():
    """Проверка виртуального окружения."""
    print("\n🔧 Проверка виртуального окружения...")
    
    if Path("venv").exists():
        print("✅ Виртуальное окружение найдено")
        return True
    else:
        print("❌ Виртуальное окружение не найдено")
        return False

def check_dependencies():
    """Проверка зависимостей."""
    print("\n📦 Проверка зависимостей...")
    
    required_packages = [
        'fdb', 'pandas', 'matplotlib', 'seaborn', 
        'plotly', 'jupyter', 'python-dotenv', 'tqdm', 'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ Отсутствуют пакеты: {', '.join(missing_packages)}")
        return False
    else:
        print("\n✅ Все зависимости установлены")
        return True

def check_database_config():
    """Проверка конфигурации базы данных."""
    print("\n🗄️ Проверка конфигурации базы данных...")
    
    config_file = Path("config.env")
    if config_file.exists():
        print("✅ Файл config.env найден")
        
        # Читаем конфигурацию
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_vars = ['DB_PATH', 'DB_USER', 'DB_PASSWORD', 'DB_CHARSET']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" in content:
                print(f"✅ {var} - настроен")
            else:
                print(f"❌ {var} - НЕ НАСТРОЕН")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️ Отсутствуют переменные: {', '.join(missing_vars)}")
            return False
        else:
            print("\n✅ Конфигурация базы данных корректна")
            return True
    else:
        print("❌ Файл config.env не найден")
        return False

def check_directories():
    """Проверка необходимых директорий."""
    print("\n📁 Проверка директорий...")
    
    required_dirs = ['src', 'logs', 'output', 'reports', 'data']
    missing_dirs = []
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/ - OK")
        else:
            print(f"❌ {directory}/ - НЕ НАЙДЕНА")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n⚠️ Отсутствуют директории: {', '.join(missing_dirs)}")
        return False
    else:
        print("\n✅ Все директории найдены")
        return True

def main():
    """Главная функция проверки системы."""
    print("Проверка системы Coffee Sales Analysis Tool...")
    
    checks = [
        check_python_version,
        check_virtual_environment,
        check_dependencies,
        check_database_config,
        check_directories
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📈 Результаты проверки: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("🎉 Система готова к работе!")
        return 0
    else:
        print("⚠️ Требуется настройка системы!")
        print("\n📋 Рекомендации:")
        print("1. Запустите install.py для установки зависимостей")
        print("2. Настройте config.env с параметрами базы данных")
        print("3. Создайте необходимые директории")
        return 1

if __name__ == "__main__":
    sys.exit(main())

