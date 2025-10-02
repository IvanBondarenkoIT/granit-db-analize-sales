"""
Основной скрипт для анализа продаж кофе
"""
import sys
import os
from datetime import datetime, timedelta
from src.database_connector import DatabaseConnector
from src.coffee_analysis import CoffeeAnalysis


def main():
    """Основная функция"""
    print("АНАЛИЗ ПРОДАЖ КОФЕ - ГРАНИТ ДБ")
    print("=" * 50)
    
    # Проверяем подключение к БД
    print("Подключение к базе данных...")
    with DatabaseConnector() as db:
        if not db.test_connection():
            print("ОШИБКА: Не удалось подключиться к базе данных!")
            return
        
        print("УСПЕХ: Подключение к БД успешно!")
        
        # Создаем анализатор
        analyzer = CoffeeAnalysis(db)
        
        # Параметры анализа
        print("\nНастройка параметров анализа...")
        
        # Можно изменить эти параметры
        store_ids = [27, 43, 44, 46, 33, 45]  # Активные магазины
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # Последний год
        
        print(f"Период анализа: {start_date} - {end_date}")
        print(f"Магазины: {store_ids}")
        
        # Загружаем данные
        print("\nЗагрузка данных...")
        analyzer.load_data(
            store_ids=store_ids,
            start_date=start_date,
            end_date=end_date
        )
        
        # Выводим общую сводку
        print("\nОБЩАЯ СВОДКА:")
        print("-" * 30)
        summary = analyzer.get_sales_summary()
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value:,}" if isinstance(value, (int, float)) else f"{key}: {value}")
        
        # Анализ по магазинам
        print("\nПРОДАЖИ ПО МАГАЗИНАМ:")
        print("-" * 30)
        store_sales = analyzer.sales_by_store()
        print(store_sales)
        
        # Топ товары
        print("\nТОП-10 ТОВАРОВ:")
        print("-" * 30)
        top_products = analyzer.sales_by_product(10)
        print(top_products)
        
        # Создаем отчеты
        print("\nСоздание отчетов...")
        
        # Создаем директории
        os.makedirs('output', exist_ok=True)
        os.makedirs('reports', exist_ok=True)
        
        # Статические графики
        print("Создание статических графиков...")
        analyzer.create_sales_charts('output')
        
        # Интерактивный дашборд
        print("Создание интерактивного дашборда...")
        analyzer.create_interactive_dashboard('output')
        
        # Экспорт в Excel
        print("Экспорт данных в Excel...")
        analyzer.export_to_excel('output')
        
        print("\nАНАЛИЗ ЗАВЕРШЕН!")
        print("Результаты сохранены в папке 'output':")
        print("  - sales_by_store.png - График продаж по магазинам")
        print("  - top_products.png - График топ товаров")
        print("  - sales_by_month.png - График продаж по месяцам")
        print("  - coffee_dashboard.html - Интерактивный дашборд")
        print("  - coffee_analysis.xlsx - Детальный отчет в Excel")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nАнализ прерван пользователем")
    except Exception as e:
        print(f"\nОШИБКА: {e}")
        sys.exit(1)
