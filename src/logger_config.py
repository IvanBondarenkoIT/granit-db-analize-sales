"""
Конфигурация логирования для приложения
"""
import logging
import os
from datetime import datetime

def setup_logger(name="coffee_analysis", level=logging.DEBUG):
    """
    Настройка логгера для приложения
    
    Args:
        name: Имя логгера
        level: Уровень логирования
        
    Returns:
        logging.Logger: Настроенный логгер
    """
    # Создаем директорию для логов
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Очищаем существующие обработчики
    logger.handlers.clear()
    
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Обработчик для файла
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f"coffee_analysis_{datetime.now().strftime('%Y%m%d')}.log"),
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name="coffee_analysis"):
    """Получить логгер по имени"""
    return logging.getLogger(name)

