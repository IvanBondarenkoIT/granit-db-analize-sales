#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Release Script

Создание релиза приложения.
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def create_release_directory():
    """Создание директории для релиза."""
    print("📦 Создание релиза...")
    
    # Создаем имя релиза
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_name = f"coffee-sales-analysis-{timestamp}"
    release_dir = Path("releases") / release_name
    
    # Создаем директорию
    release_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Создана директория {release_dir}")
    
    return release_dir

def copy_source_files(release_dir):
    """Копирование исходных файлов."""
    print("\n📋 Копирование исходных файлов...")
    
    # Файлы для копирования
    files_to_copy = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py",
        "requirements.txt", "config.env", "README.md"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, release_dir)
            print(f"✅ Скопирован {file_name}")
        else:
            print(f"⚠️ Файл {file_name} не найден")
    
    # Директории для копирования
    dirs_to_copy = ["src", "docs", "scripts"]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, release_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
        else:
            print(f"⚠️ Директория {dir_name} не найдена")

def create_install_script(release_dir):
    """Создание скрипта установки для релиза."""
    print("\n🔧 Создание скрипта установки...")
    
    install_script = release_dir / "install_release.py"
    
    with open(install_script, 'w', encoding='utf-8') as f:
        f.write('''#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Release Installer

Установка релиза приложения.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Установка релиза."""
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
    
    print(f"✅ Создан {install_script}")

def create_readme(release_dir):
    """Создание README для релиза."""
    print("\n📖 Создание README для релиза...")
    
    readme_content = f"""# Coffee Sales Analysis Tool - Release

Версия: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Установка

1. Запустите: `python install_release.py`
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
    
    with open(release_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README создан")

def create_archive(release_dir):
    """Создание архива релиза."""
    print("\n📦 Создание архива...")
    
    try:
        # Создаем ZIP архив
        archive_name = f"{release_dir.name}.zip"
        shutil.make_archive(
            str(release_dir.parent / release_dir.stem),
            'zip',
            str(release_dir.parent),
            release_dir.name
        )
        
        print(f"✅ Создан архив {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")
        return None

def main():
    """Главная функция создания релиза."""
    print("🚀 Создание релиза Coffee Sales Analysis Tool...")
    
    try:
        # Создаем директорию релиза
        release_dir = create_release_directory()
        
        # Копируем файлы
        copy_source_files(release_dir)
        
        # Создаем скрипт установки
        create_install_script(release_dir)
        
        # Создаем README
        create_readme(release_dir)
        
        # Создаем архив
        archive_name = create_archive(release_dir)
        
        print(f"\n🎉 Релиз создан успешно!")
        print(f"📁 Директория: {release_dir}")
        if archive_name:
            print(f"📦 Архив: {archive_name}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при создании релиза: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

