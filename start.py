#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Background Launcher

Запуск приложения в фоновом режиме.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Запуск приложения в фоне."""
    print("🚀 Запуск Coffee Sales Analysis Tool в фоновом режиме...")
    
    # Определяем команду запуска
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        python_cmd = "venv/bin/python"
    
    # Запуск GUI приложения
    try:
        subprocess.Popen([python_cmd, "run_gui.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        print("✅ Приложение запущено в фоновом режиме!")
        print("📱 GUI интерфейс должен открыться в новом окне")
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

