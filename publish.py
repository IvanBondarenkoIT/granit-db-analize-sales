#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Publish Script

Публикация проекта.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

def create_publication_directory():
    """Создание директории для публикации."""
    print("📦 Создание директории публикации...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    publish_dir = Path("publications") / f"coffee-sales-analysis-{timestamp}"
    
    # Создаем директорию
    publish_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Создана директория {publish_dir}")
    
    return publish_dir

def copy_publication_files(publish_dir):
    """Копирование файлов для публикации."""
    print("\n📋 Копирование файлов для публикации...")
    
    # Основные файлы
    files_to_copy = [
        "main.py", "run_gui.py", "run_console.py", "run_with_logs.py",
        "test_app.py", "install.py", "update.py", "check_system.py",
        "clean.py", "start.py", "stop.py", "release.py", "monitor.py",
        "setup.py", "upgrade.py", "docs.py", "build.py", "deploy.py",
        "version.py", "package.py", "publish.py", "requirements.txt",
        "config.env", "README.md", ".gitignore"
    ]
    
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, publish_dir)
            print(f"✅ Скопирован {file_name}")
        else:
            print(f"⚠️ Файл {file_name} не найден")
    
    # Директории
    dirs_to_copy = ["src", "docs", "scripts", "tests"]
    
    for dir_name in dirs_to_copy:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, publish_dir / dir_name)
            print(f"✅ Скопирована директория {dir_name}")
        else:
            print(f"⚠️ Директория {dir_name} не найден")

def create_publication_readme(publish_dir):
    """Создание README для публикации."""
    print("\n📖 Создание README для публикации...")
    
    readme_content = f"""# Coffee Sales Analysis Tool

Версия: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Описание

Coffee Sales Analysis Tool - это GUI приложение для анализа продаж кофе из базы данных Firebird с корректными расчетами сумм, чашек и килограммов.

## Возможности

- **Подключение к БД Firebird** - безопасное подключение с проверкой
- **Анализ продаж кофе** - расчет чашек, килограммов и сумм
- **Гибкие отчеты** - группировка по дням/неделям/месяцам
- **Экспорт в Excel** - сохранение результатов
- **Система логирования** - отладка и мониторинг

## Установка

1. Клонируйте репозиторий
2. Перейдите в директорию проекта
3. Запустите установку:
   ```bash
   python install.py
   ```

## Настройка

Отредактируйте файл `config.env`:

```env
DB_PATH=D:\\Granit DB\\GEORGIA.GDB
DB_USER=SYSDBA
DB_PASSWORD=masterkey
DB_CHARSET=UTF8
```

## Запуск

### GUI приложение
```bash
python main.py
# или
python run_gui.py
```

### Консольное приложение
```bash
python run_console.py
```

### С логами
```bash
python run_with_logs.py
```

## Структура проекта

```
coffee-sales-analysis/
├── src/                    # Исходный код
│   ├── database_connector.py
│   ├── gui_app.py
│   ├── logger_config.py
│   └── coffee_analysis.py
├── tests/                  # Тестовые скрипты
├── scripts/                # Скрипты запуска
├── docs/                   # Документация
├── data/                   # Данные для сверки
├── logs/                   # Логи приложения
├── output/                 # Результаты экспорта
├── reports/                # Отчеты
├── notebooks/              # Jupyter notebooks
├── venv/                   # Виртуальное окружение
├── config.env              # Настройки БД
├── requirements.txt        # Зависимости Python
├── main.py                # Точка входа
└── README.md              # Документация
```

## Требования

- Python 3.8 или выше
- Windows 10/11 или Linux
- 4 GB RAM (рекомендуется 8 GB)
- 1 GB свободного места на диске

## Зависимости

- fdb - для работы с Firebird
- pandas - для анализа данных
- matplotlib - для визуализации
- seaborn - для статистических графиков
- plotly - для интерактивных графиков
- tkinter - для GUI (встроен в Python)
- python-dotenv - для работы с .env файлами
- tqdm - для прогресс-баров
- openpyxl - для работы с Excel

## Лицензия

Проект создан для внутреннего использования компании "Дом Кофе".

## Поддержка

Для получения поддержки:

1. Проверьте логи приложения
2. Обратитесь к документации
3. Создайте issue в репозитории

## Авторы

- Разработчик: AI Assistant
- Компания: Дом Кофе
- Дата создания: 2025-10-02
"""
    
    with open(publish_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README создан")

def create_publication_archive(publish_dir):
    """Создание архива публикации."""
    print("\n📦 Создание архива публикации...")
    
    try:
        # Создаем ZIP архив
        archive_name = f"{publish_dir.name}.zip"
        shutil.make_archive(
            str(publish_dir.parent / publish_dir.stem),
            'zip',
            str(publish_dir.parent),
            publish_dir.name
        )
        
        print(f"✅ Создан архив {archive_name}")
        return archive_name
        
    except Exception as e:
        print(f"❌ Ошибка при создании архива: {e}")
        return None

def create_publication_checksum(publish_dir):
    """Создание контрольной суммы публикации."""
    print("\n🔐 Создание контрольной суммы...")
    
    try:
        import hashlib
        
        # Создаем контрольную сумму для всех файлов
        checksum_file = publish_dir / "checksum.txt"
        
        with open(checksum_file, 'w', encoding='utf-8') as f:
            f.write(f"# Coffee Sales Analysis Tool - Checksums\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Вычисляем контрольные суммы для всех файлов
            for file_path in publish_dir.rglob("*"):
                if file_path.is_file() and file_path.name != "checksum.txt":
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        md5_hash = hashlib.md5(content).hexdigest()
                        sha256_hash = hashlib.sha256(content).hexdigest()
                        
                        relative_path = file_path.relative_to(publish_dir)
                        f.write(f"{relative_path}\n")
                        f.write(f"  MD5:    {md5_hash}\n")
                        f.write(f"  SHA256: {sha256_hash}\n\n")
        
        print("✅ Создана контрольная сумма")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания контрольной суммы: {e}")
        return False

def create_publication_manifest(publish_dir):
    """Создание манифеста публикации."""
    print("\n📋 Создание манифеста публикации...")
    
    manifest_file = publish_dir / "MANIFEST.txt"
    
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(f"""# Coffee Sales Analysis Tool - Publication Manifest

Package: Coffee Sales Analysis Tool
Version: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Publication Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Platform: Cross-platform
Python: 3.8+

## Description

Coffee Sales Analysis Tool - это GUI приложение для анализа продаж кофе из базы данных Firebird с корректными расчетами сумм, чашек и килограммов.

## Features

- Database connection to Firebird
- Coffee sales analysis
- Flexible reporting
- Excel export
- Logging system

## Files

""")
        
        # Добавляем информацию о файлах
        for file_path in sorted(publish_dir.rglob("*")):
            if file_path.is_file():
                relative_path = file_path.relative_to(publish_dir)
                size = file_path.stat().st_size
                f.write(f"{relative_path} ({size} bytes)\n")
    
    print("✅ Создан манифест публикации")

def create_publication_license(publish_dir):
    """Создание лицензии для публикации."""
    print("\n📄 Создание лицензии...")
    
    license_file = publish_dir / "LICENSE"
    
    with open(license_file, 'w', encoding='utf-8') as f:
        f.write("""# Coffee Sales Analysis Tool - License

Copyright (c) 2025 Дом Кофе

## Лицензия

Этот проект создан для внутреннего использования компании "Дом Кофе" и не предназначен для публичного распространения.

## Ограничения

- Запрещено копирование без разрешения
- Запрещено распространение третьим лицам
- Запрещено использование в коммерческих целях
- Запрещено изменение без уведомления авторов

## Поддержка

Для получения поддержки обращайтесь к авторам проекта.

## Контакты

- Компания: Дом Кофе
- Email: support@domcoffee.com
- Телефон: +7 (XXX) XXX-XX-XX

## Дата

2025-10-02
""")
    
    print("✅ Создана лицензия")

def main():
    """Главная функция публикации."""
    print("📦 Публикация Coffee Sales Analysis Tool...")
    
    try:
        # Создаем директорию публикации
        publish_dir = create_publication_directory()
        
        # Копируем файлы
        copy_publication_files(publish_dir)
        
        # Создаем README
        create_publication_readme(publish_dir)
        
        # Создаем манифест
        create_publication_manifest(publish_dir)
        
        # Создаем лицензию
        create_publication_license(publish_dir)
        
        # Создаем контрольную сумму
        create_publication_checksum(publish_dir)
        
        # Создаем архив
        archive_name = create_publication_archive(publish_dir)
        
        print(f"\n🎉 Публикация подготовлена успешно!")
        print(f"📁 Директория публикации: {publish_dir}")
        if archive_name:
            print(f"📦 Архив: {archive_name}")
        
        print("\n📋 Содержимое публикации:")
        print("- Исходный код (src/)")
        print("- Документация (docs/)")
        print("- Скрипты (scripts/)")
        print("- Тесты (tests/)")
        print("- Конфигурация (config.env)")
        print("- Зависимости (requirements.txt)")
        print("- README (README.md)")
        print("- Манифест (MANIFEST.txt)")
        print("- Лицензия (LICENSE)")
        print("- Контрольная сумма (checksum.txt)")
        
        print("\n📋 Следующие шаги:")
        print("1. Проверьте содержимое публикации")
        print("2. Загрузите архив на сервер")
        print("3. Опубликуйте в репозитории")
        print("4. Создайте релиз")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при подготовке публикации: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

