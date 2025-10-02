#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРОВЕРКА ФАЙЛОВ ПРОЕКТА
"""

import os
import sys

def check_project_files():
    """Проверяет наличие всех необходимых файлов проекта"""
    print("=== ПРОВЕРКА ФАЙЛОВ ПРОЕКТА ===")
    print(f"Текущая директория: {os.getcwd()}")
    print()
    
    # Список необходимых файлов
    required_files = [
        "run_gui_with_logs.py",
        "launch_gui.ps1", 
        "launch_gui.bat",
        "config.env",
        "requirements.txt",
        "src/__init__.py",
        "src/database_connector.py",
        "src/gui_app.py",
        "src/logger_config.py",
        "ЗАПУСК_ПРИЛОЖЕНИЯ.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"OK {file_path}")
        else:
            missing_files.append(file_path)
            print(f"NO {file_path}")
    
    print()
    print(f"Найдено файлов: {len(existing_files)}/{len(required_files)}")
    
    if missing_files:
        print(f"Отсутствует файлов: {len(missing_files)}")
        print("Отсутствующие файлы:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("ВСЕ ФАЙЛЫ НА МЕСТЕ!")
        return True

def check_database_path():
    """Проверяет путь к базе данных"""
    print("\n=== ПРОВЕРКА БАЗЫ ДАННЫХ ===")
    
    db_path = r"D:\Granit DB\GEORGIA.GDB"
    if os.path.exists(db_path):
        print(f"OK База данных найдена: {db_path}")
        return True
    else:
        print(f"NO База данных не найдена: {db_path}")
        print("Проверьте, что файл базы данных существует по указанному пути")
        return False

def check_python_modules():
    """Проверяет доступность Python модулей"""
    print("\n=== ПРОВЕРКА PYTHON МОДУЛЕЙ ===")
    
    required_modules = [
        "fdb",
        "pandas", 
        "tkinter",
        "matplotlib",
        "seaborn",
        "plotly",
        "jupyter",
        "dotenv",
        "tqdm",
        "openpyxl"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"OK {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"NO {module}")
    
    if missing_modules:
        print(f"\nОтсутствует модулей: {len(missing_modules)}")
        print("Установите недостающие модули:")
        print("pip install " + " ".join(missing_modules))
        return False
    else:
        print("\nВСЕ МОДУЛИ УСТАНОВЛЕНЫ!")
        return True

def main():
    """Основная функция"""
    print("ПРОВЕРКА ГОТОВНОСТИ ПРОЕКТА К ЗАПУСКУ")
    print("=" * 50)
    
    files_ok = check_project_files()
    db_ok = check_database_path()
    modules_ok = check_python_modules()
    
    print("\n" + "=" * 50)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    
    if files_ok and db_ok and modules_ok:
        print("ПРОЕКТ ГОТОВ К ЗАПУСКУ!")
        print("\nСпособы запуска:")
        print("1. PowerShell: .\\launch_gui.ps1")
        print("2. Батч-файл: launch_gui.bat")
        print("3. Ручной: python run_gui_with_logs.py")
    else:
        print("ПРОЕКТ НЕ ГОТОВ К ЗАПУСКУ!")
        print("\nИсправьте найденные проблемы и повторите проверку.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
