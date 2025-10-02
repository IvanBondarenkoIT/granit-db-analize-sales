#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Installation Script

Скрипт для установки зависимостей и настройки проекта.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Выполнение команды с выводом результата."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} завершено успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при {description}: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def main():
    """Главная функция установки."""
    print("🚀 Установка Coffee Sales Analysis Tool...")
    
    # Проверка Python
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        return 1
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} обнаружен")
    
    # Создание виртуального окружения
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Создание виртуального окружения"):
            return 1
    else:
        print("✅ Виртуальное окружение уже существует")
    
    # Активация виртуального окружения и установка зависимостей
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Установка зависимостей
    if not run_command(f"{pip_cmd} install --upgrade pip", "Обновление pip"):
        return 1
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Установка зависимостей"):
        return 1
    
    # Создание необходимых директорий
    directories = ["logs", "output", "reports", "data"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Директория {directory} создана")
    
    print("\n🎉 Установка завершена успешно!")
    print("\n📋 Следующие шаги:")
    print("1. Отредактируйте config.env с настройками базы данных")
    print("2. Запустите приложение: python main.py")
    print("3. Или GUI: python run_gui.py")
    print("4. Или с логами: python run_with_logs.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

