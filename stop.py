#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Stop Script

Остановка всех процессов приложения.
"""

import sys
import os
import subprocess
import psutil

def main():
    """Остановка всех процессов приложения."""
    print("🛑 Остановка Coffee Sales Analysis Tool...")
    
    # Поиск и остановка процессов Python, связанных с нашим приложением
    stopped_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = ' '.join(proc.info['cmdline'])
                if any(app in cmdline for app in ['main.py', 'run_gui.py', 'run_with_logs.py']):
                    print(f"🔄 Остановка процесса {proc.info['pid']}: {cmdline}")
                    proc.terminate()
                    stopped_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if stopped_count > 0:
        print(f"✅ Остановлено {stopped_count} процессов")
    else:
        print("ℹ️ Процессы приложения не найдены")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

