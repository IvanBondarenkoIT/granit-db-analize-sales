"""
Тестирование нового SQL запроса с группировкой по типам кофе
"""
from src.database_connector import DatabaseConnector
from datetime import datetime, timedelta

def test_coffee_sales_by_type():
    """Тестирование нового метода получения данных"""
    with DatabaseConnector() as db:
        if db.connect():
            print("УСПЕХ: Подключение к БД установлено!")
            
            # Тестируем новый метод
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            print(f"\nТестирование за период: {start_date} - {end_date}")
            
            # Получаем данные по типам кофе
            sales_data = db.get_coffee_sales_by_type(
                store_ids=[27, 43, 44, 46],  # Основные магазины
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"\nЗагружено {len(sales_data)} записей")
            print("\nПервые 10 записей:")
            print(sales_data.head(10))
            
            # Статистика по типам кофе
            print("\nСтатистика по типам кофе:")
            print(f"Всего чашек: {sales_data['ALLCUP'].sum():.0f}")
            print(f"MonoCup: {sales_data['MONOCUP'].sum():.0f}")
            print(f"BlendCup: {sales_data['BLENDCUP'].sum():.0f}")
            print(f"CaotinaCup: {sales_data['CAOTINACUP'].sum():.0f}")
            print(f"Общая сумма: {sales_data['TOTAL_SUM'].sum():.2f}")
            
            # Статистика по магазинам
            print("\nСтатистика по магазинам:")
            store_stats = sales_data.groupby('STORE_NAME').agg({
                'ALLCUP': 'sum',
                'MONOCUP': 'sum',
                'BLENDCUP': 'sum',
                'CAOTINACUP': 'sum',
                'TOTAL_SUM': 'sum'
            }).round(2)
            print(store_stats)
            
        else:
            print("ОШИБКА: Не удалось подключиться к БД!")

if __name__ == "__main__":
    test_coffee_sales_by_type()
