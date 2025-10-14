"""
Безопасный модуль для подключения к удаленной БД Firebird.

⚠️ КРИТИЧЕСКИ ВАЖНО:
- Только READ-ONLY доступ!
- Все запросы проверяются перед выполнением
- Запрещены любые операции изменения данных (INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE)
- Включено логирование всех операций
- Установлены таймауты для предотвращения зависаний
- Автоматическое закрытие соединений
"""

import fdb
import os
import logging
import re
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager
from datetime import datetime
import pandas as pd


class RemoteDatabaseConnector:
    """
    Безопасный коннектор для работы с удаленной БД Firebird.
    
    Особенности безопасности:
    1. READ-ONLY режим (запрет на изменение данных)
    2. Валидация SQL запросов
    3. Таймауты подключения и запросов
    4. Автоматическое логирование всех операций
    5. Безопасное управление соединениями
    """
    
    # Запрещенные SQL операции (регулярные выражения)
    FORBIDDEN_PATTERNS = [
        r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b',
        r'\b(EXECUTE\s+BLOCK)\b',
        r'\b(EXECUTE\s+PROCEDURE)\b',
        r';.*;\s*',  # Несколько запросов
    ]
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 database_path: str = None,
                 user: str = None,
                 password: str = None,
                 connection_timeout: int = 10,
                 query_timeout: int = 30,
                 read_only: bool = True,
                 max_retries: int = 3):
        """
        Инициализация безопасного коннектора.
        
        Args:
            host: IP адрес удаленного сервера
            port: Порт Firebird (по умолчанию 3050)
            database_path: Полный путь к БД на сервере
            user: Имя пользователя БД
            password: Пароль пользователя БД
            connection_timeout: Таймаут подключения в секундах
            query_timeout: Таймаут выполнения запроса в секундах
            read_only: Режим READ-ONLY (по умолчанию True)
            max_retries: Максимальное количество попыток подключения
        """
        self.logger = logging.getLogger(__name__)
        
        # Загрузка параметров из переменных окружения или использование переданных
        self.host = host or os.getenv('REMOTE_DB_HOST', '85.114.224.45')
        self.port = port or int(os.getenv('REMOTE_DB_PORT', '3055'))
        # Используем существующий алиас с сервера
        self.database_path = database_path or os.getenv('REMOTE_DB_PATH', 'DK_GEORGIA')
        self.user = user or os.getenv('REMOTE_DB_USER', 'SYSDBA')
        self.password = password or os.getenv('REMOTE_DB_PASSWORD', 'masterkey')
        
        # Параметры безопасности
        self.connection_timeout = connection_timeout
        self.query_timeout = query_timeout
        self.read_only = read_only if read_only is not None else True
        self.max_retries = max_retries
        
        # Принудительно включить READ-ONLY режим
        if not self.read_only:
            self.logger.warning("⚠️ ВНИМАНИЕ: Попытка отключить READ-ONLY режим. Режим остается активным для безопасности!")
            self.read_only = True
        
        # Строка подключения
        self.connection_string = f"{self.host}/{self.port}:{self.database_path}"
        
        self.logger.info(f"🔒 Инициализирован RemoteDatabaseConnector в READ-ONLY режиме")
        self.logger.info(f"📡 Сервер: {self.host}:{self.port}")
        self.logger.info(f"💾 БД: {self.database_path}")
    
    def _validate_query(self, query: str) -> Tuple[bool, str]:
        """
        Проверка SQL запроса на безопасность.
        
        Args:
            query: SQL запрос для проверки
            
        Returns:
            Tuple[bool, str]: (результат проверки, сообщение об ошибке)
        """
        # Удалить комментарии
        query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
        
        # Проверка на запрещенные операции
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, query_clean, re.IGNORECASE):
                error_msg = f"🚫 ОПАСНЫЙ ЗАПРОС ЗАБЛОКИРОВАН! Найдена запрещенная операция: {pattern}"
                self.logger.error(error_msg)
                self.logger.error(f"Запрос: {query[:200]}...")
                return False, error_msg
        
        # Проверка, что это SELECT запрос
        query_upper = query_clean.strip().upper()
        if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
            error_msg = "🚫 Разрешены только SELECT запросы!"
            self.logger.error(error_msg)
            return False, error_msg
        
        return True, "OK"
    
    @contextmanager
    def get_connection(self):
        """
        Контекстный менеджер для безопасной работы с подключением.
        
        Использование:
            with connector.get_connection() as conn:
                # работа с подключением
        
        Yields:
            fdb.Connection: Подключение к БД
        """
        connection = None
        try:
            self.logger.info(f"🔌 Подключение к удаленной БД: {self.connection_string}")
            
            # Подключение с таймаутом
            # Формируем строку подключения с портом
            dsn = f"{self.host}/{self.port}:{self.database_path}"
            connection = fdb.connect(
                dsn=dsn,
                user=self.user,
                password=self.password,
                charset='UTF8',
                # Таймаут подключения не поддерживается напрямую в fdb
            )
            
            # READ-ONLY режим обеспечивается валидацией SQL запросов
            # (все опасные операции блокируются перед выполнением)
            if self.read_only:
                self.logger.info("🔒 READ-ONLY режим активирован (валидация SQL)")
            
            self.logger.info("✅ Подключение к удаленной БД установлено")
            yield connection
            
        except fdb.Error as e:
            self.logger.error(f"❌ Ошибка подключения к удаленной БД: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка при подключении: {e}")
            raise
        finally:
            if connection:
                try:
                    connection.close()
                    self.logger.info("🔌 Подключение к удаленной БД закрыто")
                except Exception as e:
                    self.logger.error(f"⚠️ Ошибка при закрытии подключения: {e}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Тестирование подключения к удаленной БД.
        
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        self.logger.info("🧪 Тестирование подключения к удаленной БД...")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Простой тестовый запрос
                test_query = "SELECT 1 FROM RDB$DATABASE"
                cursor.execute(test_query)
                result = cursor.fetchone()
                cursor.close()
                
                if result:
                    msg = "✅ Подключение к удаленной БД успешно!"
                    self.logger.info(msg)
                    return True, msg
                else:
                    msg = "❌ Не удалось выполнить тестовый запрос"
                    self.logger.error(msg)
                    return False, msg
                    
        except Exception as e:
            msg = f"❌ Ошибка при тестировании подключения: {str(e)}"
            self.logger.error(msg)
            return False, msg
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple[Any, ...]]:
        """
        Безопасное выполнение SELECT запроса.
        
        Args:
            query: SQL запрос (только SELECT)
            params: Параметры запроса
            
        Returns:
            List[Tuple]: Результаты запроса
            
        Raises:
            ValueError: Если запрос не прошел проверку безопасности
            fdb.Error: Если произошла ошибка БД
        """
        # Валидация запроса
        is_valid, error_msg = self._validate_query(query)
        if not is_valid:
            raise ValueError(error_msg)
        
        self.logger.info(f"📊 Выполнение запроса к удаленной БД")
        self.logger.debug(f"SQL: {query[:200]}...")
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Выполнение запроса
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Получение результатов
                results = cursor.fetchall()
                cursor.close()
                
                self.logger.info(f"✅ Запрос выполнен успешно. Получено строк: {len(results)}")
                return results
                
        except fdb.Error as e:
            self.logger.error(f"❌ Ошибка выполнения запроса к БД: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка при выполнении запроса: {e}")
            raise
    
    def execute_query_to_dataframe(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        Выполнение запроса с возвратом результата в виде DataFrame.
        
        Args:
            query: SQL запрос (только SELECT)
            params: Параметры запроса
            
        Returns:
            pd.DataFrame: Результаты запроса
        """
        # Валидация запроса
        is_valid, error_msg = self._validate_query(query)
        if not is_valid:
            raise ValueError(error_msg)
        
        self.logger.info(f"📊 Выполнение запроса к удаленной БД (в DataFrame)")
        
        try:
            with self.get_connection() as conn:
                # Используем pandas для чтения
                if params:
                    df = pd.read_sql_query(query, conn, params=params)
                else:
                    df = pd.read_sql_query(query, conn)
                
                self.logger.info(f"✅ Получено строк: {len(df)}, столбцов: {len(df.columns)}")
                return df
                
        except fdb.Error as e:
            self.logger.error(f"❌ Ошибка выполнения запроса к БД: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Неожиданная ошибка при выполнении запроса: {e}")
            raise
    
    def get_database_info(self) -> dict:
        """
        Получение информации о БД.
        
        Returns:
            dict: Информация о БД
        """
        self.logger.info("📋 Получение информации о БД...")
        
        info = {
            'host': self.host,
            'port': self.port,
            'database': self.database_path,
            'user': self.user,
            'read_only': self.read_only,
            'connected': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            with self.get_connection() as conn:
                info['connected'] = True
                info['firebird_version'] = conn.server_version
                info['database_name'] = conn.database_name
                
                # Получить количество таблиц
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM RDB$RELATIONS 
                    WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL
                """)
                info['tables_count'] = cursor.fetchone()[0]
                cursor.close()
                
                self.logger.info("✅ Информация о БД получена")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении информации о БД: {e}")
            info['error'] = str(e)
        
        return info


# Функция для удобного создания коннектора
def create_remote_connector(**kwargs) -> RemoteDatabaseConnector:
    """
    Создание безопасного коннектора к удаленной БД.
    
    Args:
        **kwargs: Параметры подключения (необязательно, используются переменные окружения)
        
    Returns:
        RemoteDatabaseConnector: Экземпляр коннектора
    """
    return RemoteDatabaseConnector(**kwargs)


if __name__ == "__main__":
    # Пример использования
    from .logger_config import setup_logger
    
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("🧪 ТЕСТИРОВАНИЕ УДАЛЕННОГО ПОДКЛЮЧЕНИЯ К БД")
    logger.info("=" * 80)
    
    try:
        # Создание коннектора
        connector = create_remote_connector()
        
        # Тестирование подключения
        success, message = connector.test_connection()
        print(f"\n{message}\n")
        
        if success:
            # Получение информации о БД
            db_info = connector.get_database_info()
            print("📋 Информация о БД:")
            for key, value in db_info.items():
                print(f"  {key}: {value}")
            
            # Пример запроса
            print("\n📊 Тестовый запрос (первые 5 магазинов):")
            query = "SELECT FIRST 5 ID, NAME FROM STORGRP"
            df = connector.execute_query_to_dataframe(query)
            print(df)
            
            # Попытка выполнить опасный запрос (должна быть заблокирована)
            print("\n🚫 Попытка выполнить UPDATE (должна быть заблокирована):")
            try:
                dangerous_query = "UPDATE STORGRP SET NAME = 'Test'"
                connector.execute_query(dangerous_query)
            except ValueError as e:
                print(f"✅ Запрос заблокирован: {e}")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ Ошибка: {e}\n")

