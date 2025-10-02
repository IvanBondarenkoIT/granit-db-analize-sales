#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Setup Script

Настройка проекта и создание конфигурации.
"""

import os
import sys
from pathlib import Path

def create_directories():
    """Создание необходимых директорий."""
    print("📁 Создание директорий...")
    
    directories = [
        "logs", "output", "reports", "data", "notebooks",
        "tests", "scripts", "docs", "releases"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Создана директория {directory}/")

def create_config():
    """Создание конфигурационного файла."""
    print("\n⚙️ Создание конфигурации...")
    
    config_file = Path("config.env")
    
    if config_file.exists():
        print("ℹ️ Файл config.env уже существует")
        return
    
    config_content = """# Coffee Sales Analysis Tool - Configuration
# Настройки подключения к базе данных Firebird

# Путь к базе данных
DB_PATH=D:\\Granit DB\\GEORGIA.GDB

# Пользователь базы данных
DB_USER=SYSDBA

# Пароль базы данных
DB_PASSWORD=masterkey

# Кодировка базы данных
DB_CHARSET=UTF8

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
        f.write(config_content)
    
    print("✅ Создан файл config.env")

def create_gitignore():
    """Создание .gitignore файла."""
    print("\n🔒 Создание .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
logs/*.log
output/*
reports/*
data/*.xlsx
data/*.csv
*.db
*.sqlite
*.sqlite3

# Config
config.env
.env
.secrets

# Temporary files
*.tmp
*.temp
*.bak
*.orig
*.rej

# Jupyter Notebook
.ipynb_checkpoints

# pytest
.pytest_cache/
.coverage
htmlcov/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("✅ Создан файл .gitignore")

def create_requirements():
    """Создание requirements.txt."""
    print("\n📦 Создание requirements.txt...")
    
    requirements_content = """# Coffee Sales Analysis Tool - Dependencies

# Database
fdb>=2.0.0

# Data Analysis
pandas>=1.5.0
numpy>=1.21.0

# Visualization
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0

# GUI
tkinter  # Built-in with Python

# Utilities
python-dotenv>=0.19.0
tqdm>=4.64.0
openpyxl>=3.0.0

# Development
jupyter>=1.0.0
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0

# System
psutil>=5.9.0
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    print("✅ Создан файл requirements.txt")

def create_launch_scripts():
    """Создание скриптов запуска."""
    print("\n🚀 Создание скриптов запуска...")
    
    # Windows batch файлы
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    # start.bat
    start_bat = scripts_dir / "start.bat"
    with open(start_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo Starting Coffee Sales Analysis Tool...
cd /d "%~dp0.."
call venv\\Scripts\\activate
python main.py
pause
""")
    
    # start_gui.bat
    start_gui_bat = scripts_dir / "start_gui.bat"
    with open(start_gui_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo Starting Coffee Sales Analysis Tool GUI...
cd /d "%~dp0.."
call venv\\Scripts\\activate
python run_gui.py
pause
""")
    
    # start_with_logs.bat
    start_logs_bat = scripts_dir / "start_with_logs.bat"
    with open(start_logs_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
echo Starting Coffee Sales Analysis Tool with logs...
cd /d "%~dp0.."
call venv\\Scripts\\activate
python run_with_logs.py
pause
""")
    
    # PowerShell скрипты
    start_ps1 = scripts_dir / "start.ps1"
    with open(start_ps1, 'w', encoding='utf-8') as f:
        f.write("""# Coffee Sales Analysis Tool - Start Script
Write-Host "Starting Coffee Sales Analysis Tool..." -ForegroundColor Green
Set-Location $PSScriptRoot\\..
& .\\venv\\Scripts\\Activate.ps1
python main.py
Read-Host "Press Enter to continue"
""")
    
    print("✅ Созданы скрипты запуска")

def main():
    """Главная функция настройки."""
    print("⚙️ Настройка Coffee Sales Analysis Tool...")
    
    try:
        create_directories()
        create_config()
        create_gitignore()
        create_requirements()
        create_launch_scripts()
        
        print("\n🎉 Настройка завершена успешно!")
        print("\n📋 Следующие шаги:")
        print("1. Отредактируйте config.env с настройками базы данных")
        print("2. Запустите install.py для установки зависимостей")
        print("3. Запустите check_system.py для проверки системы")
        print("4. Запустите main.py для запуска приложения")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при настройке: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

