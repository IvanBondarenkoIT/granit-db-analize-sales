#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Deploy Script

Развертывание приложения.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def create_deployment_package():
    """Создание пакета для развертывания."""
    print("📦 Создание пакета для развертывания...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_dir = Path("deploy") / f"coffee-sales-analysis-{timestamp}"
    
    # Создаем директорию
    deploy_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Создана директория {deploy_dir}")
    
    return deploy_dir

def copy_deployment_files(deploy_dir):
    """Копирование файлов для развертывания."""
    print("\n📋 Копирование файлов для развертывания...")
    
    # Основные файлы
    files_to_copy = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py", "monitor.py",
        "setup.py", "upgrade.py", "docs.py", "build.py", "deploy.py",
        "requirements.txt", "config.env", "README.md", ".gitignore"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, deploy_dir)
            print(f"✅ Скопирован {file_name}")
        else:
            print(f"⚠️ Файл {file_name} не найден")
    
    # Директории
    dirs_to_copy = ["src", "docs", "scripts", "tests"]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, deploy_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
        else:
            print(f"⚠️ Директория {dir_name} не найдена")

def create_deployment_script(deploy_dir):
    """Создание скрипта развертывания."""
    print("\n🔧 Создание скрипта развертывания...")
    
    deploy_script = deploy_dir / "deploy.py"
    
    with open(deploy_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Deployment Script

Развертывание приложения на целевом сервере.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Развертывание приложения."""
    print("🚀 Развертывание Coffee Sales Analysis Tool...")
    
    # Создание виртуального окружения
    if not Path("venv").exists():
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Виртуальное окружение создано")
    
    # Активация и установка зависимостей
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        pip_cmd = "venv/bin/pip"
    
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
    print("✅ Зависимости установлены")
    
    # Создание директорий
    for directory in ["logs", "output", "reports", "data"]:
        Path(directory).mkdir(exist_ok=True)
    
    # Настройка конфигурации
    if not Path("config.env").exists():
        print("⚠️ Файл config.env не найден!")
        print("Скопируйте config.env.example в config.env и настройте его")
        return 1
    
    print("🎉 Развертывание завершено!")
    print("Запуск: python main.py")

if __name__ == "__main__":
    main()
''')
    
    print("✅ Создан скрипт развертывания")

def create_dockerfile(deploy_dir):
    """Создание Dockerfile."""
    print("\n🐳 Создание Dockerfile...")
    
    dockerfile_content = """FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание необходимых директорий
RUN mkdir -p logs output reports data

# Установка прав доступа
RUN chmod +x *.py

# Открытие порта
EXPOSE 8000

# Команда запуска
CMD ["python", "main.py"]
"""
    
    with open(deploy_dir / "Dockerfile", 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    
    print("✅ Создан Dockerfile")

def create_docker_compose(deploy_dir):
    """Создание docker-compose.yml."""
    print("\n🐳 Создание docker-compose.yml...")
    
    compose_content = """version: '3.8'

services:
  coffee-sales-analysis:
    build: .
    container_name: coffee-sales-analysis
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./output:/app/output
      - ./reports:/app/reports
    environment:
      - DB_PATH=/app/data/GEORGIA.GDB
      - DB_USER=SYSDBA
      - DB_PASSWORD=masterkey
      - DB_CHARSET=UTF8
    restart: unless-stopped
    networks:
      - coffee-network

networks:
  coffee-network:
    driver: bridge
"""
    
    with open(deploy_dir / "docker-compose.yml", 'w', encoding='utf-8') as f:
        f.write(compose_content)
    
    print("✅ Создан docker-compose.yml")

def create_install_script(deploy_dir):
    """Создание скрипта установки."""
    print("\n🔧 Создание скрипта установки...")
    
    install_script = deploy_dir / "install.sh"
    
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write('''#!/bin/bash
# Coffee Sales Analysis Tool - Installation Script

echo "🚀 Installing Coffee Sales Analysis Tool..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required!"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create directories
mkdir -p logs output reports data
echo "✅ Directories created"

# Set permissions
chmod +x *.py
echo "✅ Permissions set"

echo "🎉 Installation completed!"
echo "Run: python main.py"
''')
    
    # Устанавливаем права на выполнение
    os.chmod(install_script, 0o755)
    print("✅ Создан скрипт установки")

def create_windows_installer(deploy_dir):
    """Создание Windows установщика."""
    print("\n🪟 Создание Windows установщика...")
    
    installer_script = deploy_dir / "install.bat"
    
    with open(installer_script, 'w', encoding='utf-8') as f:
        f.write('''@echo off
echo Installing Coffee Sales Analysis Tool...

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found

REM Create virtual environment
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
call venv\\Scripts\\activate

REM Install dependencies
pip install -r requirements.txt
echo Dependencies installed

REM Create directories
if not exist "logs" mkdir logs
if not exist "output" mkdir output
if not exist "reports" mkdir reports
if not exist "data" mkdir data
echo Directories created

echo Installation completed!
echo Run: python main.py
pause
''')
    
    print("✅ Создан Windows установщик")

def create_archive(deploy_dir):
    """Создание архива развертывания."""
    print("\n📦 Создание архива развертывания...")
    
    try:
        # Создаем ZIP архив
        archive_name = f"{deploy_dir.name}.zip"
        shutil.make_archive(
            str(deploy_dir.parent / deploy_dir.stem),
            'zip',
            str(deploy_dir.parent),
            deploy_dir.name
        )
        
        print(f"✅ Создан архив {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")
        return None

def main():
    """Главная функция развертывания."""
    print("🚀 Развертывание Coffee Sales Analysis Tool...")
    
    try:
        # Создаем пакет развертывания
        deploy_dir = create_deployment_package()
        
        # Копируем файлы
        copy_deployment_files(deploy_dir)
        
        # Создаем скрипты
        create_deployment_script(deploy_dir)
        create_dockerfile(deploy_dir)
        create_docker_compose(deploy_dir)
        create_install_script(deploy_dir)
        create_windows_installer(deploy_dir)
        
        # Создаем архив
        archive_name = create_archive(deploy_dir)
        
        print(f"\n🎉 Развертывание подготовлено успешно!")
        print(f"📁 Директория развертывания: {deploy_dir}")
        if archive_name:
            print(f"📦 Архив: {archive_name}")
        
        print("\n📋 Инструкции по развертыванию:")
        print("1. Скопируйте архив на целевой сервер")
        print("2. Распакуйте архив")
        print("3. Запустите install.sh (Linux) или install.bat (Windows)")
        print("4. Настройте config.env")
        print("5. Запустите приложение")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при подготовке развертывания: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

