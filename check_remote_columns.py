"""Быстрая проверка колонок в удаленной БД"""

import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.remote_db_connector import RemoteDatabaseConnector

print("=" * 80)
print("ПРОВЕРКА КОЛОНОК ТАБЛИЦЫ STORZAKAZDT")
print("=" * 80)

try:
    connector = RemoteDatabaseConnector()
    
    # Тест подключения
    success, msg = connector.test_connection()
    if not success:
        print(f"Ошибка подключения: {msg}")
        sys.exit(1)
    
    print("✅ Подключение успешно\n")
    
    # Получить первую запись чтобы увидеть все колонки
    query = "SELECT FIRST 1 * FROM STORZAKAZDT WHERE DAT_ >= '2025-09-01'"
    
    df = connector.execute_query_to_dataframe(query)
    
    print("📋 Все колонки в таблице STORZAKAZDT:")
    print("-" * 80)
    for i, col in enumerate(df.columns, 1):
        print(f"{i:3d}. {col}")
    
    print("\n" + "=" * 80)
    print(f"Всего колонок: {len(df.columns)}")
    print("=" * 80)
    
    # Проверим конкретные колонки
    print("\n🔍 Проверка наличия нужных колонок:")
    needed = ['ALLCUP', 'CASH', 'DAT_', 'STORGRPID', 'CSDTKTHBID']
    for col in needed:
        exists = col in df.columns
        status = "✅" if exists else "❌"
        print(f"{status} {col}")
    
    # Покажем пример данных
    if len(df) > 0:
        print("\n📊 Пример первой записи:")
        print("-" * 80)
        for col in df.columns:
            print(f"{col}: {df.iloc[0][col]}")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()

