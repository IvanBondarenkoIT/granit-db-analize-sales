"""Проверка структуры таблицы STORZAKAZDT в удаленной БД"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.remote_db_connector import RemoteDatabaseConnector
from src.logger_config import setup_logger

logger = setup_logger()

print("=" * 80)
print("ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ STORZAKAZDT В УДАЛЕННОЙ БД")
print("=" * 80)

try:
    # Создание коннектора
    connector = RemoteDatabaseConnector()
    
    # Тест подключения
    success, message = connector.test_connection()
    if not success:
        print(f"❌ Ошибка подключения: {message}")
        sys.exit(1)
    
    print("✅ Подключение успешно\n")
    
    # Получить структуру таблицы
    print("📋 Структура таблицы STORZAKAZDT:")
    print("-" * 80)
    
    query = """
    SELECT 
        RDB$FIELD_NAME as FIELD_NAME,
        RDB$FIELD_POSITION as POSITION
    FROM RDB$RELATION_FIELDS
    WHERE RDB$RELATION_NAME = 'STORZAKAZDT'
    ORDER BY RDB$FIELD_POSITION
    """
    
    df = connector.execute_query_to_dataframe(query)
    
    for idx, row in df.iterrows():
        field_name = row['FIELD_NAME'].strip()
        position = row['POSITION']
        print(f"{position:3d}. {field_name}")
    
    print("\n" + "=" * 80)
    print(f"Всего полей: {len(df)}")
    print("=" * 80)
    
    # Проверим, есть ли поля связанные с чашками
    print("\n🔍 Поиск полей связанных с чашками/количеством:")
    print("-" * 80)
    
    cup_fields = df[df['FIELD_NAME'].str.contains('CUP|QUANTITY|QTY|COUNT|AMOUNT', case=False, na=False)]
    
    if len(cup_fields) > 0:
        print("Найдены поля:")
        for idx, row in cup_fields.iterrows():
            print(f"  - {row['FIELD_NAME'].strip()}")
    else:
        print("❌ Поля с 'CUP' не найдены")
        print("\nВсе поля таблицы:")
        for idx, row in df.iterrows():
            print(f"  - {row['FIELD_NAME'].strip()}")
    
    # Попробуем получить пример данных
    print("\n📊 Пример данных из таблицы (первые 3 записи):")
    print("-" * 80)
    
    sample_query = """
    SELECT FIRST 3 *
    FROM STORZAKAZDT
    WHERE DAT_ >= '2025-09-01'
    """
    
    try:
        sample_df = connector.execute_query_to_dataframe(sample_query)
        print(f"Колонки: {', '.join(sample_df.columns.tolist())}")
        print(f"\nПервая запись:")
        if len(sample_df) > 0:
            for col in sample_df.columns:
                print(f"  {col}: {sample_df.iloc[0][col]}")
    except Exception as e:
        print(f"❌ Ошибка получения примера: {e}")
    
except Exception as e:
    logger.error(f"Ошибка: {e}")
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Проверка завершена!")

