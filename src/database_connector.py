"""
Модуль для подключения к базе данных Firebird
"""
import fdb
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, date

# Загружаем переменные окружения
load_dotenv('config.env')


class DatabaseConnector:
    """Класс для работы с базой данных Firebird"""
    
    def __init__(self, db_path: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Инициализация подключения к БД
        
        Args:
            db_path: Путь к файлу базы данных
            user: Имя пользователя
            password: Пароль
        """
        self.db_path = db_path or os.getenv('DB_PATH')
        self.user = user or os.getenv('DB_USER', 'SYSDBA')
        self.password = password or os.getenv('DB_PASSWORD', 'masterkey')
        self.charset = os.getenv('DB_CHARSET', 'UTF8')
        self.connection = None
        
    def connect(self) -> bool:
        """
        Подключение к базе данных
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        try:
            self.connection = fdb.connect(
                dsn=self.db_path,
                user=self.user,
                password=self.password,
                charset=self.charset
            )
            print(f"УСПЕХ: Подключение к БД успешно: {self.db_path}")
            return True
        except Exception as e:
            print(f"ОШИБКА: Ошибка подключения к БД: {e}")
            return False
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Отключение от БД")
    
    def test_connection(self) -> bool:
        """
        Тестирование подключения
        
        Returns:
            bool: True если подключение работает, False иначе
        """
        if not self.connection:
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM STORZAKAZDT")
            result = cursor.fetchone()
            print(f"УСПЕХ: Тест подключения успешен. Записей в STORZAKAZDT: {result[0]}")
            cursor.close()
            return True
        except Exception as e:
            print(f"ОШИБКА: Ошибка тестирования подключения: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Выполнение SQL запроса и возврат результата в виде DataFrame
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            pd.DataFrame: Результат запроса
        """
        if not self.connection:
            raise Exception("Нет подключения к БД. Вызовите connect() сначала.")
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Получаем названия колонок
            columns = [desc[0] for desc in cursor.description]
            
            # Получаем данные
            data = cursor.fetchall()
            
            cursor.close()
            
            # Создаем DataFrame
            df = pd.DataFrame(data, columns=columns)
            return df
            
        except Exception as e:
            print(f"ОШИБКА: Ошибка выполнения запроса: {e}")
            raise
    
    def get_sales_data(self, 
                      store_ids: Optional[List[int]] = None,
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение данных о продажах
        
        Args:
            store_ids: Список ID магазинов
            start_date: Начальная дата (YYYY-MM-DD)
            end_date: Конечная дата (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Данные о продажах
        """
        # Параметры по умолчанию
        if store_ids is None:
            store_ids = [27, 43, 44, 46, 33, 45]  # Активные магазины
        
        if start_date is None:
            start_date = '2018-01-01'
            
        if end_date is None:
            end_date = '2025-12-31'
        
        query = """
        SELECT 
            s.GODSID,
            g.NAME as GOOD_NAME,
            s.SOURCE as QUANTITY,
            s.PRICE,
            (s.SOURCE * s.PRICE) as TOTAL_SUM,
            sz.DAT_ as ORDER_DATE,
            sg.NAME as STORE_NAME,
            sz.STORGRPID as STORE_ID,
            gg.NAME as GROUP_NAME
        FROM STORZDTGDS s
        JOIN STORZAKAZDT sz ON s.SZID = sz.ID
        JOIN GOODS g ON s.GODSID = g.ID
        LEFT JOIN STORGRP sg ON sz.STORGRPID = sg.ID
        LEFT JOIN GOODSGROUPS gg ON g.OWNER = gg.ID
        WHERE sz.STORGRPID IN ({})
        AND sz.CSDTKTHBID IN (1,2,3,5)
        AND sz.DAT_ >= ? AND sz.DAT_ <= ?
        ORDER BY g.NAME, sz.DAT_
        """.format(','.join(['?' for _ in store_ids]))
        
        params = store_ids + [start_date, end_date]
        return self.execute_query(query, params)
    
    def get_coffee_products(self) -> pd.DataFrame:
        """
        Получение списка товаров с кофе
        
        Returns:
            pd.DataFrame: Список товаров с кофе
        """
        query = """
        SELECT g.ID, g.NAME, g.OWNER, gg.NAME as GROUP_NAME,
               CASE 
                   WHEN g.OWNER IN ('24435','25539','21671','25546','25775','25777','25789') THEN 'MonoCup'
                   WHEN g.OWNER IN ('23076','21882','25767','248882','25788') THEN 'BlendCup'
                   WHEN g.OWNER IN ('24491','21385') THEN 'CaotinaCup'
                   ELSE 'Other'
               END as COFFEE_TYPE
        FROM GOODS g
        LEFT JOIN GOODSGROUPS gg ON g.OWNER = gg.ID
        WHERE g.OWNER IN ('24435','25539','21671','25546','25775','25777','25789',
                          '23076','21882','25767','248882','25788',
                          '24491','21385')
        ORDER BY g.NAME
        """
        return self.execute_query(query)
    
    def get_stores_info(self) -> pd.DataFrame:
        """
        Получение информации о магазинах
        
        Returns:
            pd.DataFrame: Информация о магазинах
        """
        query = """
        SELECT ID, NAME
        FROM STORGRP
        ORDER BY NAME
        """
        return self.execute_query(query)
    
    def get_sales_statistics(self, 
                            store_ids: Optional[List[int]] = None,
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение статистики продаж по магазинам
        
        Args:
            store_ids: Список ID магазинов
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            pd.DataFrame: Статистика продаж
        """
        if store_ids is None:
            store_ids = [27, 43, 44, 46, 33, 45]
        
        if start_date is None:
            start_date = '2018-01-01'
            
        if end_date is None:
            end_date = '2025-12-31'
        
        query = """
        SELECT 
            sz.STORGRPID,
            sg.NAME as STORE_NAME,
            COUNT(*) as ORDERS_COUNT,
            SUM(s.SOURCE * s.PRICE) as TOTAL_SUM,
            AVG(s.SOURCE * s.PRICE) as AVG_ORDER_VALUE
        FROM STORZDTGDS s
        JOIN STORZAKAZDT sz ON s.SZID = sz.ID
        LEFT JOIN STORGRP sg ON sz.STORGRPID = sg.ID
        WHERE sz.STORGRPID IN ({})
        AND sz.CSDTKTHBID IN (1,2,3,5)
        AND sz.DAT_ >= ? AND sz.DAT_ <= ?
        GROUP BY sz.STORGRPID, sg.NAME
        ORDER BY TOTAL_SUM DESC
        """.format(','.join(['?' for _ in store_ids]))
        
        params = store_ids + [start_date, end_date]
        return self.execute_query(query, params)
    
    def get_coffee_sales_by_type(self, 
                                store_ids: Optional[List[int]] = None,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение продаж кофе с группировкой по типам (MonoCup, BlendCup, CaotinaCup)
        
        Args:
            store_ids: Список ID магазинов
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            pd.DataFrame: Данные о продажах по типам кофе
        """
        if store_ids is None:
            store_ids = [27, 43, 44, 46, 33, 45]
        
        if start_date is None:
            start_date = '2018-01-01'
            
        if end_date is None:
            end_date = '2025-12-31'
        
        query = """
        SELECT stgp.name as STORE_NAME,
               SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789') 
                        THEN GD.Source ELSE 0 END) AS MonoCup,
               SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') 
                        THEN GD.Source ELSE 0 END) AS BlendCup,
               SUM(CASE WHEN G.OWNER IN ('24491','21385') 
                        THEN GD.Source ELSE 0 END) AS CaotinaCup,
               SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789',
                                        '23076','21882','25767','248882','25788',
                                        '24491','21385') 
                        THEN GD.Source ELSE 0 END) AS AllCup,
               SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789',
                                        '23076','21882','25767','248882','25788',
                                        '24491','21385') 
                        THEN GD.Source * GD.PRICE ELSE 0 END) AS TOTAL_SUM,
               D.DAT_ as ORDER_DATE
        FROM storzakazdt D
        JOIN STORZDTGDS GD ON D.ID = GD.SZID 
        JOIN Goods G ON GD.GodsID = G.ID
        JOIN storgrp stgp ON D.storgrpid = stgp.id
        LEFT JOIN goodsgroups GG ON G.owner = GG.id
        WHERE D.STORGRPID IN ({})
        AND D.CSDTKTHBID IN ('1', '2', '3','5')
        AND D.DAT_ >= ? AND D.DAT_ <= ?
        AND NOT (
            D.comment LIKE '%мы;%' OR
            D.comment LIKE '%Мы;%' OR
            D.comment LIKE '%Тестирование%')
        GROUP BY stgp.name, D.DAT_
        ORDER BY stgp.name, D.DAT_
        """.format(','.join(['?' for _ in store_ids]))
        
        params = store_ids + [start_date, end_date]
        return self.execute_query(query, params)
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        self.disconnect()


if __name__ == "__main__":
    # Тестирование подключения
    with DatabaseConnector() as db:
        if db.test_connection():
            print("🎉 Подключение к базе данных работает!")
            
            # Получаем информацию о магазинах
            stores = db.get_stores_info()
            print(f"\n📊 Магазины в базе данных:")
            print(stores)
            
            # Получаем товары с кофе
            coffee_products = db.get_coffee_products()
            print(f"\n☕ Товары с кофе (первые 10):")
            print(coffee_products.head(10))
