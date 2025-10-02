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
        self._is_connected = False
        self._connection_attempts = 0
        self._max_connection_attempts = 3
        
    def connect(self) -> bool:
        """
        Безопасное подключение к базе данных с повторными попытками
        
        Returns:
            bool: True если подключение успешно, False иначе
        """
        if self._is_connected and self.connection:
            try:
                # Проверяем, что соединение еще активно
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                cursor.close()
                return True
            except:
                # Соединение разорвано, сбрасываем флаг
                self._is_connected = False
                self.connection = None
        
        if not self.db_path:
            print("ОШИБКА: Не указан путь к базе данных")
            return False
            
        if not os.path.exists(self.db_path):
            print(f"ОШИБКА: Файл базы данных не найден: {self.db_path}")
            return False
        
        for attempt in range(self._max_connection_attempts):
            try:
                self._connection_attempts += 1
                print(f"Попытка подключения {self._connection_attempts}/{self._max_connection_attempts}...")
                
                self.connection = fdb.connect(
                    dsn=self.db_path,
                    user=self.user,
                    password=self.password,
                    charset=self.charset
                )
                
                # Тестируем соединение
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                cursor.close()
                
                self._is_connected = True
                print(f"УСПЕХ: Подключение к БД успешно: {self.db_path}")
                return True
                
            except Exception as e:
                print(f"ОШИБКА: Попытка {self._connection_attempts} не удалась: {e}")
                if self.connection:
                    try:
                        self.connection.close()
                    except:
                        pass
                    self.connection = None
                
                if attempt < self._max_connection_attempts - 1:
                    print("Повторная попытка через 2 секунды...")
                    import time
                    time.sleep(2)
        
        print(f"ОШИБКА: Не удалось подключиться к БД после {self._max_connection_attempts} попыток")
        return False
    
    def disconnect(self):
        """Безопасное отключение от базы данных"""
        if self.connection:
            try:
                # Проверяем, что соединение еще активно
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1 FROM RDB$DATABASE")
                cursor.close()
                
                # Закрываем соединение
                self.connection.close()
                print("УСПЕХ: Отключение от БД успешно")
            except Exception as e:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Ошибка при отключении от БД: {e}")
            finally:
                self.connection = None
                self._is_connected = False
        else:
            print("ИНФО: Соединение с БД уже закрыто")
    
    def test_connection(self) -> bool:
        """
        Безопасное тестирование подключения
        
        Returns:
            bool: True если подключение работает, False иначе
        """
        if not self.connection or not self._is_connected:
            print("ИНФО: Нет активного соединения с БД")
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM RDB$DATABASE")
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0] == 1:
                print("УСПЕХ: Тест подключения к БД прошел успешно")
                return True
            else:
                print("ОШИБКА: Неожиданный результат теста подключения")
                return False
                
        except Exception as e:
            print(f"ОШИБКА: Ошибка тестирования подключения: {e}")
            self._is_connected = False
            return False
    
    def execute_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """
        Безопасное выполнение SQL запроса и возврат результата в виде DataFrame
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            pd.DataFrame: Результат запроса
        """
        if not self.connection or not self._is_connected:
            raise Exception("Нет активного подключения к БД. Вызовите connect() сначала.")
        
        cursor = None
        try:
            # Проверяем соединение перед выполнением запроса
            test_cursor = self.connection.cursor()
            test_cursor.execute("SELECT 1 FROM RDB$DATABASE")
            test_cursor.close()
            
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Получаем названия колонок
            columns = [desc[0] for desc in cursor.description]
            
            # Получаем данные
            data = cursor.fetchall()
            
            # Создаем DataFrame
            df = pd.DataFrame(data, columns=columns)
            return df
            
        except Exception as e:
            print(f"ОШИБКА: Ошибка выполнения запроса: {e}")
            # Сбрасываем флаг подключения при ошибке
            self._is_connected = False
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
    
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
    
    def get_coffee_sales_with_packages(self, 
                                     store_ids: Optional[List[int]] = None,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Получение продаж кофе с правильным расчетом килограммов (пачки кофе + пачки Caotina)
        
        Args:
            store_ids: Список ID магазинов
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            pd.DataFrame: Данные о продажах с чашками, килограммами и суммами
        """
        if store_ids is None:
            store_ids = [27, 43, 44, 46, 33, 45]
        
        if start_date is None:
            start_date = '2018-01-01'
            
        if end_date is None:
            end_date = '2025-12-31'
        
        # Запрос для чашек кофе
        cups_query = """
        SELECT stgp.name as STORE_NAME,
               D.DAT_ as ORDER_DATE,
               SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789') 
                        THEN GD.Source ELSE 0 END) AS MonoCup,
               SUM(CASE WHEN G.OWNER IN ('23076','21882','25767','248882','25788') 
                        THEN GD.Source ELSE 0 END) AS BlendCup,
               SUM(CASE WHEN G.OWNER IN ('24491','21385') 
                        THEN GD.Source ELSE 0 END) AS CaotinaCup,
               SUM(CASE WHEN G.OWNER IN ('24435','25539','21671','25546','25775','25777','25789',
                                        '23076','21882','25767','248882','25788',
                                        '24491','21385') 
                        THEN GD.Source ELSE 0 END) AS AllCup
        FROM storzakazdt D
        JOIN STORZDTGDS GD ON D.ID = GD.SZID 
        JOIN Goods G ON GD.GodsID = G.ID
        JOIN storgrp stgp ON D.storgrpid = stgp.id
        WHERE D.STORGRPID IN ({})
        AND D.CSDTKTHBID IN ('1', '2', '3','5')
        AND D.DAT_ >= ? AND D.DAT_ <= ?
        AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
        GROUP BY stgp.name, D.DAT_
        """.format(','.join(['?' for _ in store_ids]))
        
        # Запрос для пачек кофе и Caotina (килограммы)
        packages_query = """
        SELECT stgp.name as STORE_NAME,
               D.DAT_ as ORDER_DATE,
               SUM(GD.SOURCE) as PACKAGES_KG
        FROM storzakazdt D 
        JOIN STORZDTGDS GD ON D.ID = GD.SZID 
        JOIN Goods G ON GD.GodsID = G.ID 
        JOIN storgrp stgp ON D.storgrpid = stgp.id 
        LEFT JOIN goodsgroups GG ON G.owner = GG.id
        WHERE D.STORGRPID IN ({})
        AND D.CSDTKTHBID IN ('1', '2', '3','5') 
        AND D.DAT_ >= ? AND D.DAT_ <= ?
        AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
        AND (
            -- Пачки кофе с весом в названии
            (
                (G.NAME LIKE '%250 g%' OR G.NAME LIKE '%250г%' OR
                 G.NAME LIKE '%500 g%' OR G.NAME LIKE '%500г%' OR
                 G.NAME LIKE '%1 kg%' OR G.NAME LIKE '%1кг%' OR
                 G.NAME LIKE '%200 g%' OR G.NAME LIKE '%200г%' OR
                 G.NAME LIKE '%125 g%' OR G.NAME LIKE '%125г%' OR
                 G.NAME LIKE '%80 g%' OR G.NAME LIKE '%80г%' OR
                 G.NAME LIKE '%0.25%' OR G.NAME LIKE '%0.5%' OR
                 G.NAME LIKE '%0.2%' OR G.NAME LIKE '%0.125%' OR
                 G.NAME LIKE '%0.08%')
                AND (G.NAME LIKE '%Coffee%' OR G.NAME LIKE '%кофе%' OR 
                     G.NAME LIKE '%Кофе%' OR G.NAME LIKE '%Blaser%' OR 
                     G.NAME LIKE '%Blasercafe%')
            )
            OR
            -- Пачки Caotina
            (
                GG.NAME LIKE '%Caotina swiss chocolate drink (package)%'
            )
        )
        GROUP BY stgp.name, D.DAT_
        """.format(','.join(['?' for _ in store_ids]))
        
        # Запрос для общей кассы
        cash_query = """
        SELECT stgp.name as STORE_NAME,
               D.DAT_ as ORDER_DATE,
               SUM(D.SUMMA) as TOTAL_CASH
        FROM storzakazdt D 
        JOIN storgrp stgp ON D.storgrpid = stgp.id
        WHERE D.STORGRPID IN ({})
        AND D.CSDTKTHBID IN ('1', '2', '3','5') 
        AND D.DAT_ >= ? AND D.DAT_ <= ?
        AND NOT (D.comment LIKE '%мы;%' OR D.comment LIKE '%Мы;%' OR D.comment LIKE '%Тестирование%')
        GROUP BY stgp.name, D.DAT_
        """.format(','.join(['?' for _ in store_ids]))
        
        params = store_ids + [start_date, end_date]
        
        # Выполняем запросы
        cups_data = self.execute_query(cups_query, params)
        packages_data = self.execute_query(packages_query, params)
        cash_data = self.execute_query(cash_query, params)
        
        # Объединяем данные
        if not cups_data.empty and not packages_data.empty and not cash_data.empty:
            # Объединяем чашки и пачки
            combined = cups_data.merge(packages_data, on=['STORE_NAME', 'ORDER_DATE'], how='outer')
            # Объединяем с кассой
            result = combined.merge(cash_data, on=['STORE_NAME', 'ORDER_DATE'], how='outer')
            
            # Заполняем пропущенные значения нулями
            result = result.fillna(0)
            
            return result
        else:
            # Возвращаем пустой DataFrame с нужными колонками
            return pd.DataFrame(columns=['STORE_NAME', 'ORDER_DATE', 'MonoCup', 'BlendCup', 'CaotinaCup', 'AllCup', 'PACKAGES_KG', 'TOTAL_CASH'])
    
    def __enter__(self):
        """Контекстный менеджер - вход"""
        if not self.connect():
            raise Exception("Не удалось подключиться к базе данных")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер - выход"""
        try:
            self.disconnect()
        except Exception as e:
            print(f"ПРЕДУПРЕЖДЕНИЕ: Ошибка при закрытии соединения: {e}")
        
        # Возвращаем False, чтобы исключения не подавлялись
        return False


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
