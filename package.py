#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Package Script

Создание пакета для распространения.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def create_package_directory():
    """Создание директории для пакета."""
    print("📦 Создание директории пакета...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_dir = Path("packages") / f"coffee-sales-analysis-{timestamp}"
    
    # Создаем директорию
    package_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Создана директория {package_dir}")
    
    return package_dir

def copy_package_files(package_dir):
    """Копирование файлов для пакета."""
    print("\n📋 Копирование файлов для пакета...")
    
    # Основные файлы
    files_to_copy = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py", "monitor.py",
        "setup.py", "upgrade.py", "docs.py", "build.py", "deploy.py",
        "version.py", "package.py", "requirements.txt", "config.env",
        "README.md", ".gitignore"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, package_dir)
            print(f"✅ Скопирован {file_name}")
        else:
            print(f"⚠️ Файл {file_name} не найден")
    
    # Директории
    dirs_to_copy = ["src", "docs", "scripts", "tests"]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, package_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
        else:
            print(f"⚠️ Директория {dir_name} не найдена")

def create_package_installer(package_dir):
    """Создание установщика пакета."""
    print("\n🔧 Создание установщика пакета...")
    
    installer_script = package_dir / "install_package.py"
    
    with open(installer_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Package Installer

Установка пакета приложения.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Установка пакета."""
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
    
    # Копирование конфигурации
    if not Path("config.env").exists():
        if Path("config.env.example").exists():
            shutil.copy2("config.env.example", "config.env")
            print("✅ Конфигурация скопирована")
        else:
            print("⚠️ Файл конфигурации не найден")
    
    print("🎉 Установка пакета завершена!")
    print("Запуск: python main.py")

if __name__ == "__main__":
    main()
''')
    
    print("✅ Создан установщик пакета")

def create_package_readme(package_dir):
    """Создание README для пакета."""
    print("\n📖 Создание README для пакета...")
    
    readme_content = f"""# Coffee Sales Analysis Tool

Версия: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Установка

1. Запустите: `python install_package.py`
2. Настройте `config.env` с параметрами базы данных
3. Запустите: `python main.py`

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
    
    with open(package_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README создан")

def create_package_archive(package_dir):
    """Создание архива пакета."""
    print("\n📦 Создание архива пакета...")
    
    try:
        # Создаем ZIP архив
        archive_name = f"{package_dir.name}.zip"
        shutil.make_archive(
            str(package_dir.parent / package_dir.stem),
            'zip',
            str(package_dir.parent),
            package_dir.name
        )
        
        print(f"✅ Создан архив {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")
        return None

def create_package_checksum(package_dir):
    """Создание контрольной суммы пакета."""
    print("\n🔐 Создание контрольной суммы...")
    
    try:
        import hashlib
        
        # Создаем контрольную сумму для всех файлов
        checksum_file = package_dir / "checksum.txt"
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            f.write(f"# Coffee Sales Analysis Tool - Checksums\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Вычисляем контрольные суммы для всех файлов
            for file_path in package_dir.rglob("*"):
                if file_path.is_file() and file_path.name != "checksum.txt":
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        md5_hash = hashlib.md5(content).hexdigest()
                        sha256_hash = hashlib.sha256(content).hexdigest()
                        
                        relative_path = file_path.relative_to(package_dir)
                        f.write(f"{relative_path}\n")
                        f.write(f"  MD5:    {md5_hash}\n")
                        f.write(f"  SHA256: {sha256_hash}\n\n")
        
        print("✅ Создана контрольная сумма")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания контрольной суммы: {e}")
        return False

def create_package_manifest(package_dir):
    """Создание манифеста пакета."""
    print("\n📋 Создание манифеста пакета...")
    
    manifest_file = package_dir / "MANIFEST.txt"
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Coffee Sales Analysis Tool - Package Manifest

Package: Coffee Sales Analysis Tool
Version: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Build Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Platform: Cross-platform
Python: 3.8+

## Files

""")
        
        # Добавляем информацию о файлах
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file():
                relative_path = file_path.relative_to(package_dir)
                size = file_path.stat().st_size
                f.write(f"{relative_path} ({size} bytes)\n")
    
    print("✅ Создан манифест пакета")

def main():
    """Главная функция создания пакета."""
    print("📦 Создание пакета Coffee Sales Analysis Tool...")
    
    try:
        # Создаем директорию пакета
        package_dir = create_package_directory()
        
        # Копируем файлы
        copy_package_files(package_dir)
        
        # Создаем установщик
        create_package_installer(package_dir)
        
        # Создаем README
        create_package_readme(package_dir)
        
        # Создаем манифест
        create_package_manifest(package_dir)
        
        # Создаем контрольную сумму
        create_package_checksum(package_dir)
        
        # Создаем архив
        archive_name = create_package_archive(package_dir)
        
        print(f"\n🎉 Пакет создан успешно!")
        print(f"📁 Директория пакета: {package_dir}")
        if archive_name:
            print(f"📦 Архив: {archive_name}")
        
        print("\n📋 Содержимое пакета:")
        print("- Установщик (install_package.py)")
        print("- Исходный код (src/)")
        print("- Документация (docs/)")
        print("- Скрипты (scripts/)")
        print("- Тесты (tests/)")
        print("- Конфигурация (config.env)")
        print("- Зависимости (requirements.txt)")
        print("- README (README.md)")
        print("- Манифест (MANIFEST.txt)")
        print("- Контрольная сумма (checksum.txt)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при создании пакета: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

