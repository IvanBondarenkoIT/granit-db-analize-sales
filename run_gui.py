#!/usr/bin/env python3
"""
Coffee Sales Analysis Tool - GUI Launcher

Запуск GUI приложения с настройкой логирования.
"""

import sys
import os
from pathlib import Path

# Добавляем src в путь для импортов
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.gui_app import CoffeeAnalysisGUI
from src.logger_config import setup_logger

def main():
    """Запуск GUI приложения."""
    # Настройка логирования
    logger = setup_logger()
    logger.info("Запуск GUI приложения")
    
    try:
        # Создание и запуск GUI
        app = CoffeeAnalysisGUI()
        app.run()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске GUI: {e}")
        print(f"Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

