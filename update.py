#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Update Script

Обновление зависимостей и приложения.
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
    """Главная функция обновления."""
    print("🔄 Обновление Coffee Sales Analysis Tool...")
    
    # Определяем команды
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        pip_cmd = "venv/bin/pip"
    
    # Обновление pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Обновление pip"):
        return 1
    
    # Обновление всех зависимостей
    if not run_command(f"{pip_cmd} install --upgrade -r requirements.txt", "Обновление зависимостей"):
        return 1
    
    # Обновление pip до последней версии
    if not run_command(f"{pip_cmd} install --upgrade pip", "Финальное обновление pip"):
        return 1
    
    print("\n🎉 Обновление завершено успешно!")
    print("\n📋 Рекомендации:")
    print("1. Перезапустите приложение для применения обновлений")
    print("2. Проверьте совместимость с новой версией Python")
    print("3. Обновите базу данных при необходимости")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

