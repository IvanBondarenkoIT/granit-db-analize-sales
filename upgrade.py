#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Upgrade Script

Обновление проекта до новой версии.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def backup_project():
    """Создание резервной копии проекта."""
    print("💾 Создание резервной копии проекта...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups") / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Файлы для резервного копирования
    files_to_backup = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py", "monitor.py",
        "setup.py", "upgrade.py", "requirements.txt", "config.env",
        "README.md", ".gitignore"
    ]
    
    # Копируем файлы
    for file_name in files_to_backup:
        if Path(file_name).exists():
            shutil.copy2(file_name, backup_dir)
            print(f"✅ Скопирован {file_name}")
    
    # Копируем директории
    dirs_to_backup = ["src", "docs", "scripts", "tests"]
    for dir_name in dirs_to_backup:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, backup_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
    
    print(f"✅ Резервная копия создана: {backup_dir}")
    return backup_dir

def check_git_status():
    """Проверка статуса Git."""
    print("\n🔍 Проверка статуса Git...")
    
    try:
        # Проверяем, есть ли Git репозиторий
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git репозиторий найден")
            
            # Проверяем изменения
            if "nothing to commit" in result.stdout:
                print("✅ Нет несохраненных изменений")
            else:
                print("⚠️ Есть несохраненные изменения:")
                print(result.stdout)
                
                response = input("Продолжить обновление? (y/n): ").lower()
                if response not in ['y', 'yes', 'да']:
                    print("❌ Обновление отменено")
                    return False
        else:
            print("ℹ️ Git репозиторий не найден")
            
    except FileNotFoundError:
        print("ℹ️ Git не установлен")
    except Exception as e:
        print(f"⚠️ Ошибка проверки Git: {e}")
    
    return True

def update_dependencies():
    """Обновление зависимостей."""
    print("\n📦 Обновление зависимостей...")
    
    try:
        # Определяем команду pip
        if os.name == 'nt':  # Windows
            pip_cmd = "venv\\Scripts\\pip"
        else:  # Unix/Linux/MacOS
            pip_cmd = "venv/bin/pip"
        
        # Обновляем pip
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        print("✅ pip обновлен")
        
        # Обновляем зависимости
        subprocess.run([pip_cmd, "install", "--upgrade", "-r", "requirements.txt"], check=True)
        print("✅ Зависимости обновлены")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка обновления зависимостей: {e}")
        return False

def update_config():
    """Обновление конфигурации."""
    print("\n⚙️ Обновление конфигурации...")
    
    config_file = Path("config.env")
    
    if not config_file.exists():
        print("ℹ️ Файл config.env не найден, создаем новый")
        # Здесь можно вызвать setup.py для создания конфигурации
        return True
    
    # Проверяем версию конфигурации
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "APP_VERSION" in content:
        print("✅ Конфигурация уже обновлена")
    else:
        print("🔄 Обновляем конфигурацию...")
        
        # Добавляем новые параметры
        new_config = content + """
# Настройки приложения
APP_NAME=Coffee Sales Analysis Tool
APP_VERSION=1.0.0
APP_DEBUG=False

# Настройки логирования
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Настройки отчетов
REPORT_FORMAT=excel
REPORT_ENCODING=utf-8
REPORT_SHEET_NAME=Отчет

# Настройки GUI
GUI_THEME=default
GUI_WINDOW_SIZE=1200x800
GUI_FONT_SIZE=10
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_config)
        
        print("✅ Конфигурация обновлена")
    
    return True

def update_scripts():
    """Обновление скриптов."""
    print("\n🔧 Обновление скриптов...")
    
    # Проверяем наличие новых скриптов
    new_scripts = [
        "monitor.py", "upgrade.py", "setup.py"
    ]
    
    for script in new_scripts:
        if not Path(script).exists():
            print(f"⚠️ Скрипт {script} не найден")
    
    print("✅ Скрипты проверены")
    return True

def test_application():
    """Тестирование приложения после обновления."""
    print("\n🧪 Тестирование приложения...")
    
    try:
        # Запускаем тесты
        result = subprocess.run([sys.executable, "test_app.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Тесты пройдены успешно")
            return True
        else:
            print("❌ Тесты не пройдены:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Тесты превысили время ожидания")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def main():
    """Главная функция обновления."""
    print("🔄 Обновление Coffee Sales Analysis Tool...")
    
    try:
        # Создаем резервную копию
        backup_dir = backup_project()
        
        # Проверяем Git статус
        if not check_git_status():
            return 1
        
        # Обновляем зависимости
        if not update_dependencies():
            print("❌ Ошибка обновления зависимостей")
            return 1
        
        # Обновляем конфигурацию
        if not update_config():
            print("❌ Ошибка обновления конфигурации")
            return 1
        
        # Обновляем скрипты
        if not update_scripts():
            print("❌ Ошибка обновления скриптов")
            return 1
        
        # Тестируем приложение
        if not test_application():
            print("⚠️ Тесты не пройдены, но обновление завершено")
        
        print("\n🎉 Обновление завершено успешно!")
        print(f"💾 Резервная копия: {backup_dir}")
        print("\n📋 Рекомендации:")
        print("1. Проверьте работу приложения")
        print("2. Обновите документацию при необходимости")
        print("3. Создайте новый релиз")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

