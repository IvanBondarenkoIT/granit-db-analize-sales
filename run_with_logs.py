#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - Launcher with Console Logs

Запуск приложения с выводом логов в консоль.
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем src в путь для импортов
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.gui_app import CoffeeAnalysisGUI
from src.logger_config import setup_logger

def main():
    """Запуск приложения с логами в консоль."""
    # Настройка логирования с выводом в консоль
    logger = setup_logger()
    
    # Добавляем консольный handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info("Запуск приложения с логами в консоль")
    
    try:
        # Создание и запуск GUI
        app = CoffeeAnalysisGUI()
        app.run()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

