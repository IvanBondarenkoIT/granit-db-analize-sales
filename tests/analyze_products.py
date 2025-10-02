"""
Скрипт для анализа структуры товаров и определения весов
"""
from src.database_connector import DatabaseConnector
import re

def extract_weight_from_name(name):
    """Извлекает вес из названия товара"""
    # Ищем паттерны веса в скобках и без скобок
    patterns = [
        r'\((\d+(?:\.\d+)?)\s*kg\)',  # (1kg), (0.5kg)
        r'\((\d+(?:\.\d+)?)\s*g\)',   # (250g), (500g)
        r'\((\d+(?:\.\d+)?)\s*г\)',   # (250г)
        r'(\d+(?:\.\d+)?)\s*kg\b',    # 1kg, 0.5kg
        r'(\d+(?:\.\d+)?)\s*g\b',     # 250g, 500g
        r'(\d+(?:\.\d+)?)\s*г\b',     # 250г
        r'(\d+(?:\.\d+)?)\s*,\s*(\d+)\s*g',  # 0,500 g
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:  # Для паттерна с запятой
                weight = float(match.group(1)) + float(match.group(2)) / 1000
            else:
                weight = float(match.group(1))
            
            # Конвертируем граммы в килограммы
            if 'g' in pattern or 'г' in pattern:
                weight = weight / 1000
            return weight
    
    return None

def main():
    with DatabaseConnector() as db:
        if db.connect():
            products = db.get_coffee_products()
            print("Анализ товаров с кофе:")
            print("=" * 50)
            
            # Анализируем первые 30 товаров
            for i, row in products.head(30).iterrows():
                name = row['NAME']
                weight = extract_weight_from_name(name)
                print(f"ID: {row['ID']}")
                print(f"Название: {name}")
                print(f"Вес (кг): {weight if weight else 'Не определен'}")
                print("-" * 30)
            
            # Статистика по весам
            weights = []
            for i, row in products.iterrows():
                weight = extract_weight_from_name(row['NAME'])
                if weight:
                    weights.append(weight)
            
            print(f"\nСтатистика по весам:")
            print(f"Товаров с определенным весом: {len(weights)}")
            if weights:
                print(f"Минимальный вес: {min(weights)} кг")
                print(f"Максимальный вес: {max(weights)} кг")
                print(f"Средний вес: {sum(weights)/len(weights):.3f} кг")

if __name__ == "__main__":
    main()
