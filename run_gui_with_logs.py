"""
Запуск GUI с выводом логов в консоль
"""
import sys
import os
import logging

# Добавляем путь к модулям
sys.path.append('src')

# Настройка логирования для консоли
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """Запуск GUI с логированием в консоль"""
    print("Запуск GUI приложения с подробным логированием...")
    print("Логи будут выводиться в консоль и сохраняться в файл logs/coffee_analysis_YYYYMMDD.log")
    print("=" * 80)
    
    try:
        from src.gui_app import main as gui_main
        gui_main()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

