#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Monitor Script

Мониторинг работы приложения.
"""

import os
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime

def check_processes():
    """Проверка процессов приложения."""
    print("🔍 Проверка процессов приложения...")
    
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
        try:
            if proc.info['name'] in ['python.exe', 'python']:
                cmdline = ' '.join(proc.info['cmdline'])
                if any(app in cmdline for app in ['main.py', 'run_gui.py', 'run_with_logs.py']):
                    processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_percent']
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if processes:
        print(f"✅ Найдено {len(processes)} процессов:")
        for proc in processes:
            print(f"  PID {proc['pid']}: {proc['cmdline']}")
            print(f"    CPU: {proc['cpu']:.1f}%, Memory: {proc['memory']:.1f}%")
    else:
        print("ℹ️ Процессы приложения не найдены")
    
    return processes

def check_logs():
    """Проверка логов приложения."""
    print("\n📝 Проверка логов...")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("ℹ️ Директория logs не найдена")
        return
    
    log_files = list(logs_dir.glob("*.log"))
    if not log_files:
        print("ℹ️ Лог файлы не найдены")
        return
    
    print(f"✅ Найдено {len(log_files)} лог файлов:")
    
    for log_file in log_files:
        size = log_file.stat().st_size
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"  {log_file.name}: {size} bytes, изменен {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Показываем последние строки
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"    Последняя строка: {lines[-1].strip()}")
        except Exception as e:
            print(f"    Ошибка чтения: {e}")

def check_disk_space():
    """Проверка места на диске."""
    print("\n💾 Проверка места на диске...")
    
    try:
        disk_usage = psutil.disk_usage('.')
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        
        print(f"✅ Диск: {used_gb:.1f}GB / {total_gb:.1f}GB использовано")
        print(f"   Свободно: {free_gb:.1f}GB ({free_gb/total_gb*100:.1f}%)")
        
        if free_gb < 1:
            print("⚠️ Мало свободного места на диске!")
        
    except Exception as e:
        print(f"❌ Ошибка проверки диска: {e}")

def check_memory():
    """Проверка использования памяти."""
    print("\n🧠 Проверка памяти...")
    
    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        used_gb = memory.used / (1024**3)
        available_gb = memory.available / (1024**3)
        
        print(f"✅ Память: {used_gb:.1f}GB / {total_gb:.1f}GB использовано")
        print(f"   Доступно: {available_gb:.1f}GB ({memory.percent:.1f}%)")
        
        if memory.percent > 90:
            print("⚠️ Высокое использование памяти!")
        
    except Exception as e:
        print(f"❌ Ошибка проверки памяти: {e}")

def check_database_connection():
    """Проверка подключения к базе данных."""
    print("\n🗄️ Проверка подключения к базе данных...")
    
    try:
        # Импортируем только при необходимости
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / "src"))
        
        from src.database_connector import DatabaseConnector
        
        with DatabaseConnector() as db:
            if db.test_connection():
                print("✅ Подключение к базе данных успешно")
            else:
                print("❌ Ошибка подключения к базе данных")
                
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")

def monitor_continuous(interval=30):
    """Непрерывный мониторинг."""
    print(f"\n🔄 Запуск непрерывного мониторинга (интервал: {interval} сек)")
    print("Нажмите Ctrl+C для остановки")
    
    try:
        while True:
            print(f"\n{'='*50}")
            print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print('='*50)
            
            check_processes()
            check_logs()
            check_disk_space()
            check_memory()
            check_database_connection()
            
            print(f"\n⏰ Следующая проверка через {interval} секунд...")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен")

def main():
    """Главная функция мониторинга."""
    print("📊 Мониторинг Coffee Sales Analysis Tool...")
    
    # Разовый мониторинг
    check_processes()
    check_logs()
    check_disk_space()
    check_memory()
    check_database_connection()
    
    # Спрашиваем о непрерывном мониторинге
    try:
        response = input("\n🔄 Запустить непрерывный мониторинг? (y/n): ").lower()
        if response in ['y', 'yes', 'да']:
            interval = input("Интервал в секундах (по умолчанию 30): ").strip()
            try:
                interval = int(interval) if interval else 30
            except ValueError:
                interval = 30
            
            monitor_continuous(interval)
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())

