#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Clean Script

Очистка временных файлов и кэша.
"""

import os
import shutil
from pathlib import Path

def clean_python_cache():
    """Очистка кэша Python."""
    print("🧹 Очистка кэша Python...")
    
    # Удаление __pycache__
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                cache_path = Path(root) / dir_name
                shutil.rmtree(cache_path)
                print(f"✅ Удален {cache_path}")
    
    # Удаление .pyc файлов
    for root, dirs, files in os.walk('.'):
        for file_name in files:
            if file_name.endswith('.pyc'):
                file_path = Path(root) / file_name
                file_path.unlink()
                print(f"✅ Удален {file_path}")

def clean_logs():
    """Очистка логов."""
    print("\n📝 Очистка логов...")
    
    logs_dir = Path("logs")
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            log_file.unlink()
            print(f"✅ Удален {log_file}")
    else:
        print("ℹ️ Директория logs не найдена")

def clean_output():
    """Очистка выходных файлов."""
    print("\n📤 Очистка выходных файлов...")
    
    output_dir = Path("output")
    if output_dir.exists():
        for output_file in output_dir.glob("*"):
            if output_file.is_file():
                output_file.unlink()
                print(f"✅ Удален {output_file}")
    else:
        print("ℹ️ Директория output не найдена")

def clean_reports():
    """Очистка отчетов."""
    print("\n📊 Очистка отчетов...")
    
    reports_dir = Path("reports")
    if reports_dir.exists():
        for report_file in reports_dir.glob("*"):
            if report_file.is_file():
                report_file.unlink()
                print(f"✅ Удален {report_file}")
    else:
        print("ℹ️ Директория reports не найдена")

def clean_temp_files():
    """Очистка временных файлов."""
    print("\n🗑️ Очистка временных файлов...")
    
    temp_patterns = [
        "*.tmp", "*.temp", "*.bak", "*.swp", "*.swo",
        "*.~*", "*.orig", "*.rej", "*.log"
    ]
    
    for pattern in temp_patterns:
        for temp_file in Path(".").glob(pattern):
            if temp_file.is_file():
                temp_file.unlink()
                print(f"✅ Удален {temp_file}")

def main():
    """Главная функция очистки."""
    print("🧹 Очистка проекта Coffee Sales Analysis Tool...")
    
    try:
        clean_python_cache()
        clean_logs()
        clean_output()
        clean_reports()
        clean_temp_files()
        
        print("\n🎉 Очистка завершена успешно!")
        print("\n📋 Очищено:")
        print("- Кэш Python (__pycache__, .pyc)")
        print("- Логи приложения")
        print("- Выходные файлы")
        print("- Отчеты")
        print("- Временные файлы")
        
        return 0
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

