#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Build Script

Сборка проекта для развертывания.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def create_build_directory():
    """Создание директории для сборки."""
    print("📦 Создание директории сборки...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    build_dir = Path("build") / f"coffee-sales-analysis-{timestamp}"
    
    # Создаем директорию
    build_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Создана директория {build_dir}")
    
    return build_dir

def copy_source_files(build_dir):
    """Копирование исходных файлов."""
    print("\n📋 Копирование исходных файлов...")
    
    # Файлы для копирования
    files_to_copy = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py", "monitor.py",
        "setup.py", "upgrade.py", "docs.py", "build.py",
        "requirements.txt", "config.env", "README.md", ".gitignore"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, build_dir)
            print(f"✅ Скопирован {file_name}")
        else:
            print(f"⚠️ Файл {file_name} не найден")
    
    # Директории для копирования
    dirs_to_copy = ["src", "docs", "scripts", "tests"]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, build_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
        else:
            print(f"⚠️ Директория {dir_name} не найдена")

def create_installer(build_dir):
    """Создание установщика."""
    print("\n🔧 Создание установщика...")
    
    installer_script = build_dir / "install.py"
    
    with open(installer_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Installer

Установка приложения.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Установка приложения."""
    print("🚀 Установка Coffee Sales Analysis Tool...")
    
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
    
    print("🎉 Установка завершена!")
    print("Запуск: python main.py")

if __name__ == "__main__":
    main()
''')
    
    print("✅ Создан установщик")

def create_launcher(build_dir):
    """Создание лаунчера."""
    print("\n🚀 Создание лаунчера...")
    
    launcher_script = build_dir / "launch.py"
    
    with open(launcher_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Launcher

Запуск приложения.
"""

import sys
import os
from pathlib import Path

def main():
    """Запуск приложения."""
    print("🚀 Запуск Coffee Sales Analysis Tool...")
    
    # Проверяем виртуальное окружение
    if not Path("venv").exists():
        print("❌ Виртуальное окружение не найдено!")
        print("Запустите install.py для установки")
        return 1
    
    # Определяем команду Python
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        python_cmd = "venv/bin/python"
    
    # Запускаем приложение
    try:
        subprocess.run([python_cmd, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
''')
    
    print("✅ Создан лаунчер")

def create_readme(build_dir):
    """Создание README для сборки."""
    print("\n📖 Создание README для сборки...")
    
    readme_content = f"""# Coffee Sales Analysis Tool

Версия: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Установка

1. Запустите: `python install.py`
2. Настройте `config.env` с параметрами базы данных
3. Запустите: `python launch.py`

## Файлы

- `main.py` - Главное приложение
- `run_gui.py` - GUI приложение
- `run_console.py` - Консольное приложение
- `run_with_logs.py` - GUI с логами
- `test_app.py` - Тестирование
- `check_system.py` - Проверка системы
- `clean.py` - Очистка проекта

## Структура

- `src/` - Исходный код
- `docs/` - Документация
- `scripts/` - Скрипты запуска
- `config.env` - Настройки БД
- `requirements.txt` - Зависимости

## Поддержка

Проект создан для внутреннего использования компании "Дом Кофе".
"""
    
    with open(build_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README создан")

def create_archive(build_dir):
    """Создание архива сборки."""
    print("\n📦 Создание архива...")
    
    try:
        # Создаем ZIP архив
        archive_name = f"{build_dir.name}.zip"
        shutil.make_archive(
            str(build_dir.parent / build_dir.stem),
            'zip',
            str(build_dir.parent),
            build_dir.name
        )
        
        print(f"✅ Создан архив {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")
        return None

def create_executable():
    """Создание исполняемого файла."""
    print("\n🔨 Создание исполняемого файла...")
    
    try:
        # Проверяем наличие PyInstaller
        subprocess.run([sys.executable, "-c", "import PyInstaller"], check=True)
        
        # Создаем исполняемый файл
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "CoffeeSalesAnalysis",
            "main.py"
        ], check=True)
        
        print("✅ Исполняемый файл создан")
        return True
        
    except subprocess.CalledProcessError:
        print("⚠️ PyInstaller не установлен, пропускаем создание исполняемого файла")
        return False
    except Exception as e:
        print(f"❌ Ошибка при создании исполняемого файла: {e}")
        return False

def main():
    """Главная функция сборки."""
    print("🔨 Сборка Coffee Sales Analysis Tool...")
    
    try:
        # Создаем директорию сборки
        build_dir = create_build_directory()
        
        # Копируем файлы
        copy_source_files(build_dir)
        
        # Создаем установщик
        create_installer(build_dir)
        
        # Создаем лаунчер
        create_launcher(build_dir)
        
        # Создаем README
        create_readme(build_dir)
        
        # Создаем архив
        archive_name = create_archive(build_dir)
        
        # Создаем исполняемый файл
        create_executable()
        
        print(f"\n🎉 Сборка завершена успешно!")
        print(f"📁 Директория сборки: {build_dir}")
        if archive_name:
            print(f"📦 Архив: {archive_name}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при сборке: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

