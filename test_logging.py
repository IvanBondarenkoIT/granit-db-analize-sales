"""
Тест логирования
"""
import sys
import os
sys.path.append('src')

from src.logger_config import setup_logger

def test_logging():
    """Тест системы логирования"""
    logger = setup_logger("test_logger")
    
    logger.info("Тест логирования запущен")
    logger.debug("Отладочное сообщение")
    logger.warning("Предупреждение")
    logger.error("Тестовая ошибка")
    
    print("Логирование протестировано. Проверьте файл logs/coffee_analysis_YYYYMMDD.log")

if __name__ == "__main__":
    test_logging()

