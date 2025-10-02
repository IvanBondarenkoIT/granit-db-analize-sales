# 🗺️ АТЛАС БАЗЫ ДАННЫХ (SANITIZED VERSION)

## 📋 ОБЩАЯ ИНФОРМАЦИЯ

- **База данных**: [REDACTED].GDB
- **Версия Firebird**: 2.5.0
- **Размер файла**: 1.29 ГБ
- **Диапазон дат**: 2018-01-02 до 2025-09-30
- **Общее количество таблиц**: 366
- **Общее количество записей**: 345,526 (STORZAKAZDT)

## 🔗 ПОДКЛЮЧЕНИЕ К БД

### Параметры подключения:
```python
import fdb

# Успешные комбинации (замените на ваши):
connection_params = [
    {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
    {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
    {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
]

# Подключение:
connection = fdb.connect(
    dsn="[YOUR_DATABASE_PATH]",
    user='[YOUR_USER]',
    password='[YOUR_PASSWORD]',
    charset='UTF8'
)
```

### Проверка подключения:
```python
def test_connection():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM STORZAKAZDT")
        result = cursor.fetchone()
        print(f"✅ Подключение успешно. Записей в STORZAKAZDT: {result[0]}")
        cursor.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
```

## 🎯 ОСНОВНЫЕ ТАБЛИЦЫ

### 1. STORZDTGDS - Детали складских заказов
**Назначение**: Основная таблица с данными о товарах в складских заказах
- **Записей**: 493,554
- **Ключевые поля**:
  - `ID` - Уникальный идентификатор записи
  - `SZID` - Ссылка на складской заказ (STORZAKAZDT.ID)
  - `GODSID` - Ссылка на товар (GOODS.ID)
  - `SOURCE` - Количество товара (основное поле для аналитики)
  - `BQUANT` - Балансовое количество
  - `PRICE` - Цена товара
  - `OBJID` - Ссылка на объект

### 2. STORZAKAZDT - Складские заказы
**Назначение**: Заголовки складских заказов с датами и магазинами
- **Записей**: 354,327
- **Ключевые поля**:
  - `ID` - Уникальный идентификатор заказа
  - `STORGRPID` - Ссылка на группу складов/магазинов (STORGRP.ID)
  - `CSDTKTHBID` - Тип операции (1,2,3,5 - продажи)
  - `DAT_` - Дата заказа
  - `COMMENT` - Комментарий к заказу

### 3. GOODS - Товары
**Назначение**: Справочник товаров
- **Записей**: 10,248
- **Ключевые поля**:
  - `ID` - Уникальный идентификатор товара
  - `OWNER` - Ссылка на группу товаров (GOODSGROUPS.ID)
  - `NAME` - Название товара

### 4. STORGRP - Группы складов/магазинов
**Назначение**: Справочник магазинов
- **Записей**: 8
- **Ключевые поля**:
  - `ID` - Уникальный идентификатор магазина
  - `NAME` - Название магазина

### 5. GOODSGROUPS - Группы товаров
**Назначение**: Справочник групп товаров (типы кофе)
- **Записей**: 318
- **Ключевые поля**:
  - `ID` - Уникальный идентификатор группы
  - `NAME` - Название группы товаров

## 🏪 АКТИВНЫЕ МАГАЗИНЫ

| ID | Название |
|----|----------|
| 27 | [STORE_NAME_1] |
| 43 | [STORE_NAME_2] |
| 44 | [STORE_NAME_3] |
| 46 | [STORE_NAME_4] |
| 33 | [STORE_NAME_5] |
| 45 | [STORE_NAME_6] |

## ☕ ТИПЫ КОФЕ (GOODSGROUPS)

### Mono Cup (Single Origin):
- **ID 24435**: [PRODUCT_NAME_1]
- **ID 25539**: [PRODUCT_NAME_2]
- **ID 25546**: [PRODUCT_NAME_3]
- **ID 25775**: [PRODUCT_NAME_4]
- **ID 25777**: [PRODUCT_NAME_5]
- **ID 25789**: [PRODUCT_NAME_6]

### Blend Cup (Смешанные сорта):
- **ID 23076**: [PRODUCT_NAME_7]
- **ID 21882**: [PRODUCT_NAME_8]
- **ID 25767**: [PRODUCT_NAME_9]
- **ID 25788**: [PRODUCT_NAME_10]

### Caotina Cup (Шоколадные напитки):
- **ID 24491**: [PRODUCT_NAME_11]
- **ID 21385**: [PRODUCT_NAME_12]

## 🔗 СВЯЗИ МЕЖДУ ТАБЛИЦАМИ

```
STORZAKAZDT (заказы)
    ↓ (SZID)
STORZDTGDS (детали заказов)
    ↓ (GODSID)
GOODS (товары)
    ↓ (OWNER)
GOODSGROUPS (группы товаров)

STORZAKAZDT (заказы)
    ↓ (STORGRPID)
STORGRP (магазины)
```

## 📊 КЛЮЧЕВЫЕ SQL ЗАПРОСЫ

### 1. Получение продаж за период:
```sql
SELECT 
    s.GODSID,
    g.NAME as GOOD_NAME,
    s.SOURCE as QUANTITY,
    s.PRICE,
    (s.SOURCE * s.PRICE) as TOTAL_SUM,
    sz.DAT_ as ORDER_DATE,
    sg.NAME as STORE_NAME
FROM STORZDTGDS s
JOIN STORZAKAZDT sz ON s.SZID = sz.ID
JOIN GOODS g ON s.GODSID = g.ID
LEFT JOIN STORGRP sg ON sz.STORGRPID = sg.ID
WHERE sz.STORGRPID = ? -- ID магазина
AND sz.CSDTKTHBID IN (1,2,3,5) -- Типы операций (продажи)
AND sz.DAT_ >= ? AND sz.DAT_ <= ? -- Период
ORDER BY g.NAME, sz.DAT_
```

### 2. Поиск товаров с кофе:
```sql
SELECT g.ID, g.NAME, g.OWNER, gg.NAME as GROUP_NAME
FROM GOODS g
LEFT JOIN GOODSGROUPS gg ON g.OWNER = gg.ID
WHERE g.NAME LIKE '%Coffee%'
   OR g.NAME LIKE '%кофе%'
   OR g.NAME LIKE '%[COFFEE_BRAND]%'
ORDER BY g.NAME
```

### 3. Статистика по магазинам:
```sql
SELECT 
    sz.STORGRPID,
    sg.NAME as STORE_NAME,
    COUNT(*) as ORDERS_COUNT,
    SUM(s.SOURCE * s.PRICE) as TOTAL_SUM
FROM STORZDTGDS s
JOIN STORZAKAZDT sz ON s.SZID = sz.ID
LEFT JOIN STORGRP sg ON sz.STORGRPID = sg.ID
WHERE sz.CSDTKTHBID IN (1,2,3,5)
AND sz.DAT_ >= ? AND sz.DAT_ <= ?
GROUP BY sz.STORGRPID, sg.NAME
ORDER BY TOTAL_SUM DESC
```

## 🛠️ ГОТОВЫЕ ИНСТРУМЕНТЫ

### 1. Подключение к БД:
```python
class DatabaseConnector:
    def __init__(self, db_path: str = "[YOUR_DATABASE_PATH]"):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        connection_params = [
            {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
            {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
            {'user': '[YOUR_USER]', 'password': '[YOUR_PASSWORD]'},
        ]
        
        for params in connection_params:
            try:
                self.connection = fdb.connect(
                    dsn=self.db_path,
                    user=params['user'],
                    password=params['password'],
                    charset='UTF8'
                )
                print(f"✅ Подключение успешно с пользователем: {params['user']}")
                return True
            except Exception as e:
                print(f"⚠️ Не удалось подключиться с {params['user']}: {e}")
                continue
        
        print("❌ Не удалось подключиться к БД")
        return False
```

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Кодировка**: Всегда используйте UTF8 при подключении
2. **Типы операций**: CSDTKTHBID IN (1,2,3,5) - это продажи
3. **Даты**: Формат 'YYYY-MM-DD' в запросах
4. **Товары с кофе**: Ищите по LIKE '%Coffee%' или '%[BRAND]%'
5. **Магазины**: Используйте STORGRPID для фильтрации

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

- **Атлас БД**: `documentation/DATABASE_ATLAS.md`
