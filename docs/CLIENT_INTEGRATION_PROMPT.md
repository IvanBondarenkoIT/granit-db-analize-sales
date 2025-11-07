# 🔌 ПРОМПТ ДЛЯ ИНТЕГРАЦИИ КЛИЕНТА С PROXY API

## 🎯 Цель

После создания и деплоя Firebird DB Proxy API на Railway.com, интегрировать его в текущий проект `Granit DB analize sales`, чтобы приложение могло работать с удаленной БД через proxy вместо прямого подключения.

---

## 📁 Текущая структура проекта

```
D:\Cursor Projects\Granit DB analize sales\
├── src/
│   ├── database_connector.py       # Локальное подключение
│   ├── remote_db_connector.py      # Прямое удаленное подключение (ТЕКУЩЕЕ)
│   ├── proxy_db_connector.py       # СОЗДАТЬ - подключение через proxy
│   ├── gui_app.py
│   ├── coffee_analysis.py
│   └── logger_config.py
├── config/
│   ├── local_db.env
│   ├── remote_db.env
│   └── proxy_api.env               # СОЗДАТЬ - настройки proxy
```

---

## 🔧 ЧТО НУЖНО СОЗДАТЬ

### 1. Файл: `src/proxy_db_connector.py`

```python
"""
Коннектор для работы с БД через Proxy API.

Этот модуль предоставляет тот же интерфейс, что и remote_db_connector.py,
но вместо прямого подключения к Firebird использует REST API proxy.

Преимущества:
- Работает с любого IP адреса (не требует whitelist)
- Централизованная безопасность и аудит
- Автоматический rate limiting
- HTTPS шифрование
"""

import os
import logging
import requests
from typing import Optional, List, Tuple, Any
from datetime import datetime
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class ProxyDatabaseConnector:
    """
    Коннектор для выполнения запросов к Firebird БД через Proxy API.
    
    Использование идентично RemoteDatabaseConnector для простоты миграции.
    """
    
    def __init__(
        self,
        api_url: str = None,
        api_token: str = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Инициализация коннектора к Proxy API.
        
        Args:
            api_url: URL Proxy API (например: https://your-app.railway.app)
            api_token: Bearer Token для аутентификации
            timeout: Таймаут HTTP запросов в секундах
            max_retries: Количество повторных попыток при ошибке
        """
        self.logger = logging.getLogger(__name__)
        
        # Загрузка параметров из environment variables или использование переданных
        self.api_url = (api_url or os.getenv('PROXY_API_URL', '')).rstrip('/')
        self.api_token = api_token or os.getenv('PROXY_API_TOKEN', '')
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_url:
            raise ValueError("PROXY_API_URL не настроен! Укажите в .env файле или передайте в конструктор.")
        
        if not self.api_token:
            raise ValueError("PROXY_API_TOKEN не настроен! Укажите в .env файле или передайте в конструктор.")
        
        # Настройка HTTP сессии с retry логикой
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Заголовки для всех запросов
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        })
        
        self.logger.info(f"🔒 Инициализирован ProxyDatabaseConnector")
        self.logger.info(f"📡 Proxy API: {self.api_url}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Тестирование подключения к Proxy API и БД.
        
        Returns:
            Tuple[bool, str]: (успех, сообщение)
        """
        self.logger.info("🧪 Тестирование подключения к Proxy API...")
        
        try:
            # Запрос к health endpoint
            response = self.session.get(
                f"{self.api_url}/api/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'healthy' and data.get('database_connected'):
                msg = "✅ Подключение к Proxy API и БД успешно!"
                self.logger.info(msg)
                self.logger.info(f"   Версия API: {data.get('version', 'unknown')}")
                return True, msg
            else:
                msg = f"❌ Proxy API доступен, но БД недоступна: {data}"
                self.logger.error(msg)
                return False, msg
                
        except requests.exceptions.ConnectionError as e:
            msg = f"❌ Не удается подключиться к Proxy API: {self.api_url}"
            self.logger.error(f"{msg}\n{e}")
            return False, msg
        except requests.exceptions.Timeout:
            msg = f"❌ Таймаут подключения к Proxy API (>{self.timeout}s)"
            self.logger.error(msg)
            return False, msg
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                msg = "❌ Ошибка аутентификации: неверный API токен"
            else:
                msg = f"❌ HTTP ошибка: {e.response.status_code}"
            self.logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"❌ Неожиданная ошибка при тестировании: {str(e)}"
            self.logger.error(msg)
            return False, msg
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[dict]:
        """
        Безопасное выполнение SELECT запроса через Proxy API.
        
        Args:
            query: SQL запрос (только SELECT)
            params: Параметры запроса (tuple или list)
            
        Returns:
            List[dict]: Результаты запроса в виде списка словарей
            
        Raises:
            ValueError: Если API вернул ошибку валидации
            requests.HTTPError: Если произошла HTTP ошибка
        """
        self.logger.info(f"📊 Выполнение запроса через Proxy API")
        self.logger.debug(f"SQL: {query[:200]}...")
        
        try:
            # Подготовка запроса
            payload = {
                'query': query
            }
            
            if params:
                # Конвертировать tuple в list для JSON сериализации
                payload['params'] = list(params) if isinstance(params, tuple) else params
            
            # Отправка запроса к proxy
            response = self.session.post(
                f"{self.api_url}/api/query",
                json=payload,
                timeout=self.timeout
            )
            
            # Проверка HTTP статуса
            if response.status_code == 401:
                raise ValueError("❌ Ошибка аутентификации: неверный API токен")
            elif response.status_code == 429:
                raise ValueError("❌ Превышен лимит запросов. Подождите немного.")
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(f"❌ Ошибка валидации SQL: {error_data.get('error', 'Unknown error')}")
            
            response.raise_for_status()
            
            # Парсинг ответа
            result = response.json()
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error')
                raise ValueError(f"❌ Proxy API вернул ошибку: {error_msg}")
            
            data = result.get('data', [])
            rows_count = result.get('rows_count', len(data))
            exec_time = result.get('execution_time', 0)
            
            self.logger.info(f"✅ Запрос выполнен успешно. Получено строк: {rows_count}, время: {exec_time:.3f}s")
            
            return data
            
        except requests.exceptions.Timeout:
            error_msg = f"❌ Таймаут выполнения запроса (>{self.timeout}s)"
            self.logger.error(error_msg)
            raise TimeoutError(error_msg)
        except requests.exceptions.HTTPError as e:
            error_msg = f"❌ HTTP ошибка при выполнении запроса: {e.response.status_code}"
            self.logger.error(error_msg)
            self.logger.error(f"Response: {e.response.text[:500]}")
            raise
        except ValueError as e:
            # Ошибки валидации - пробрасываем дальше
            self.logger.error(str(e))
            raise
        except Exception as e:
            error_msg = f"❌ Неожиданная ошибка при выполнении запроса: {str(e)}"
            self.logger.error(error_msg)
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
        self.logger.info(f"📊 Выполнение запроса через Proxy API (в DataFrame)")
        
        try:
            # Получить данные как список словарей
            data = self.execute_query(query, params)
            
            # Конвертировать в DataFrame
            df = pd.DataFrame(data)
            
            self.logger.info(f"✅ Получено строк: {len(df)}, столбцов: {len(df.columns)}")
            return df
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при создании DataFrame: {e}")
            raise
    
    def get_database_info(self) -> dict:
        """
        Получение информации о БД через Proxy API.
        
        Returns:
            dict: Информация о БД
        """
        self.logger.info("📋 Получение информации о БД через Proxy API...")
        
        info = {
            'proxy_url': self.api_url,
            'connected': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Запрос к health endpoint
            response = self.session.get(
                f"{self.api_url}/api/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            
            health_data = response.json()
            info['connected'] = health_data.get('database_connected', False)
            info['proxy_status'] = health_data.get('status')
            info['proxy_version'] = health_data.get('version')
            info['proxy_uptime'] = health_data.get('uptime_seconds')
            
            # Попробовать получить список таблиц
            try:
                tables_response = self.session.get(
                    f"{self.api_url}/api/tables",
                    timeout=self.timeout
                )
                if tables_response.status_code == 200:
                    tables_data = tables_response.json()
                    info['tables_count'] = tables_data.get('count', 0)
                    info['tables'] = tables_data.get('tables', [])
            except:
                pass  # Endpoint может быть недоступен
            
            self.logger.info("✅ Информация о БД получена через Proxy")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении информации о БД: {e}")
            info['error'] = str(e)
        
        return info
    
    def close(self):
        """Закрытие HTTP сессии"""
        if self.session:
            self.session.close()
            self.logger.info("🔌 HTTP сессия закрыта")


# Функция для удобного создания коннектора
def create_proxy_connector(**kwargs) -> ProxyDatabaseConnector:
    """
    Создание коннектора к Proxy API.
    
    Args:
        **kwargs: Параметры подключения (необязательно, используются переменные окружения)
        
    Returns:
        ProxyDatabaseConnector: Экземпляр коннектора
    """
    return ProxyDatabaseConnector(**kwargs)


if __name__ == "__main__":
    # Пример использования
    from logger_config import setup_logger
    
    logger = setup_logger()
    logger.info("=" * 80)
    logger.info("🧪 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ ЧЕРЕЗ PROXY API")
    logger.info("=" * 80)
    
    try:
        # Создание коннектора
        connector = create_proxy_connector()
        
        # Тестирование подключения
        success, message = connector.test_connection()
        print(f"\n{message}\n")
        
        if success:
            # Получение информации о БД
            db_info = connector.get_database_info()
            print("📋 Информация о БД:")
            for key, value in db_info.items():
                if key != 'tables':  # Не печатать весь список таблиц
                    print(f"  {key}: {value}")
            
            # Пример запроса
            print("\n📊 Тестовый запрос (первые 5 магазинов):")
            query = "SELECT FIRST 5 ID, NAME FROM STORGRP"
            df = connector.execute_query_to_dataframe(query)
            print(df)
            
            # Закрыть сессию
            connector.close()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ Ошибка: {e}\n")
```

---

### 2. Файл: `config/proxy_api.env`

```bash
# ==================== PROXY API CONFIGURATION ====================
# URL Proxy API на Railway.com
PROXY_API_URL=https://your-app.railway.app

# Bearer Token для аутентификации
# Получить у администратора или сгенерировать при деплое proxy
PROXY_API_TOKEN=your-secret-token-here

# Таймаут HTTP запросов (секунды)
PROXY_API_TIMEOUT=30

# Количество повторных попыток при ошибке
PROXY_API_MAX_RETRIES=3

# ==================== ПРИМЕЧАНИЯ ====================
# 1. PROXY_API_URL - получите после деплоя на Railway.com
# 2. PROXY_API_TOKEN - создайте сильный токен и добавьте в Railway environment variables
# 3. Этот файл НЕ должен коммититься в Git! Добавьте в .gitignore
# 4. Для каждого пользователя/устройства создайте копию и настройте

# ==================== ГЕНЕРАЦИЯ ТОКЕНА ====================
# Для генерации безопасного токена используйте:
# Python: import secrets; print(secrets.token_urlsafe(32))
# Bash: openssl rand -base64 32
# PowerShell: -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

---

### 3. Обновить файл: `src/gui_app.py`

Добавить возможность выбора режима подключения:

```python
# В начале файла добавить импорт
from src.proxy_db_connector import create_proxy_connector

# В GUI добавить RadioButton для выбора режима:
class CoffeeAnalysisGUI:
    def __init__(self, root):
        # ... существующий код ...
        
        # Фрейм для выбора режима подключения
        connection_frame = ttk.LabelFrame(self.control_frame, text="Режим подключения", padding=10)
        connection_frame.pack(fill='x', padx=5, pady=5)
        
        self.connection_mode = tk.StringVar(value="local")
        
        ttk.Radiobutton(
            connection_frame, 
            text="Локальная БД", 
            variable=self.connection_mode, 
            value="local"
        ).pack(anchor='w')
        
        ttk.Radiobutton(
            connection_frame, 
            text="Удаленная БД (прямое подключение)", 
            variable=self.connection_mode, 
            value="remote"
        ).pack(anchor='w')
        
        ttk.Radiobutton(
            connection_frame, 
            text="Удаленная БД (через Proxy API) 🔒", 
            variable=self.connection_mode, 
            value="proxy"
        ).pack(anchor='w')
        
        # ... остальной код ...
    
    def get_connector(self):
        """Получить коннектор в зависимости от выбранного режима"""
        mode = self.connection_mode.get()
        
        if mode == "local":
            from src.database_connector import create_database_connector
            return create_database_connector()
        
        elif mode == "remote":
            from src.remote_db_connector import create_remote_connector
            return create_remote_connector()
        
        elif mode == "proxy":
            from src.proxy_db_connector import create_proxy_connector
            return create_proxy_connector()
        
        else:
            raise ValueError(f"Unknown connection mode: {mode}")
    
    def run_analysis(self):
        """Запуск анализа с выбранным коннектором"""
        try:
            connector = self.get_connector()
            
            # Тестирование подключения
            success, message = connector.test_connection()
            
            if not success:
                messagebox.showerror("Ошибка подключения", message)
                return
            
            # ... продолжение анализа ...
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
```

---

### 4. Создать скрипт: `scripts/test_proxy_connection.py`

```python
#!/usr/bin/env python
"""
Скрипт для тестирования подключения к Proxy API.
"""

import sys
import os
from pathlib import Path

# Добавить корневую директорию в PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from src.logger_config import setup_logger
from src.proxy_db_connector import create_proxy_connector

# Загрузить environment variables
load_dotenv('config/proxy_api.env')

def main():
    """Тестирование Proxy API подключения"""
    logger = setup_logger()
    
    print("=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К PROXY API")
    print("=" * 80)
    print()
    
    # Проверка настроек
    api_url = os.getenv('PROXY_API_URL')
    api_token = os.getenv('PROXY_API_TOKEN')
    
    if not api_url:
        print("❌ PROXY_API_URL не настроен!")
        print("   Отредактируйте config/proxy_api.env")
        return 1
    
    if not api_token:
        print("❌ PROXY_API_TOKEN не настроен!")
        print("   Отредактируйте config/proxy_api.env")
        return 1
    
    print(f"📡 Proxy API URL: {api_url}")
    print(f"🔑 API Token: {api_token[:10]}...{api_token[-10:]}")
    print()
    
    try:
        # Создание коннектора
        print("🔧 Создание коннектора...")
        connector = create_proxy_connector()
        
        # Тест 1: Health check
        print("\n📊 Тест 1: Health Check")
        success, message = connector.test_connection()
        print(f"   {message}")
        
        if not success:
            print("\n❌ Подключение не удалось!")
            return 1
        
        # Тест 2: Информация о БД
        print("\n📊 Тест 2: Информация о БД")
        db_info = connector.get_database_info()
        for key, value in db_info.items():
            if key != 'tables':
                print(f"   {key}: {value}")
        
        # Тест 3: Простой запрос
        print("\n📊 Тест 3: Простой SELECT запрос")
        query = "SELECT 1 AS TEST FROM RDB$DATABASE"
        results = connector.execute_query(query)
        print(f"   Результат: {results}")
        
        # Тест 4: Запрос к таблице
        print("\n📊 Тест 4: Запрос к таблице STORGRP")
        query = "SELECT FIRST 5 ID, NAME FROM STORGRP"
        df = connector.execute_query_to_dataframe(query)
        print(f"\n{df}")
        
        # Тест 5: Параметризованный запрос
        print("\n📊 Тест 5: Параметризованный запрос")
        query = "SELECT ID, NAME FROM STORGRP WHERE ID = ?"
        results = connector.execute_query(query, params=(1,))
        print(f"   Результат: {results}")
        
        # Тест 6: Попытка опасного запроса (должна быть заблокирована)
        print("\n📊 Тест 6: Попытка UPDATE (должна быть заблокирована)")
        try:
            query = "UPDATE STORGRP SET NAME = 'Test' WHERE ID = 1"
            connector.execute_query(query)
            print("   ❌ ОШИБКА: UPDATE не был заблокирован!")
        except (ValueError, Exception) as e:
            print(f"   ✅ UPDATE успешно заблокирован: {e}")
        
        # Закрыть соединение
        connector.close()
        
        print("\n" + "=" * 80)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 80)
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Ошибка: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

---

### 5. Обновить файл: `requirements.txt`

Добавить зависимости для HTTP клиента:

```txt
# ... существующие зависимости ...

# HTTP client для Proxy API
requests==2.31.0
urllib3==2.1.0
```

---

### 6. Обновить файл: `.gitignore`

```gitignore
# ... существующие строки ...

# Proxy API credentials
config/proxy_api.env

# Не игнорировать примеры
!config/proxy_api.env.example
```

---

### 7. Создать файл: `config/proxy_api.env.example`

```bash
# ==================== PROXY API CONFIGURATION (ПРИМЕР) ====================
# Скопируйте этот файл в proxy_api.env и заполните реальными значениями

# URL Proxy API на Railway.com
PROXY_API_URL=https://your-app.railway.app

# Bearer Token для аутентификации
PROXY_API_TOKEN=your-secret-token-here

# Таймаут HTTP запросов (секунды)
PROXY_API_TIMEOUT=30

# Количество повторных попыток при ошибке
PROXY_API_MAX_RETRIES=3
```

---

### 8. Обновить файл: `docs/README.md`

Добавить раздел о Proxy API:

```markdown
# ☕ Coffee Sales Analysis Tool

## 🔌 Режимы подключения к БД

### 1. Локальная БД
Прямое подключение к локальному файлу БД Firebird.

**Настройка:** `config/local_db.env`

### 2. Удаленная БД (прямое подключение)
Прямое подключение к удаленному Firebird серверу.

**Требования:**
- Ваш IP должен быть в whitelist сервера
- Доступ к порту 3055

**Настройка:** `config/remote_db.env`

### 3. 🆕 Удаленная БД (через Proxy API) 🔒 **РЕКОМЕНДУЕТСЯ**
Подключение через безопасный REST API Gateway на Railway.com.

**Преимущества:**
- ✅ Работает с любого IP адреса
- ✅ Не требует whitelist
- ✅ HTTPS шифрование
- ✅ Централизованная безопасность
- ✅ Автоматический аудит запросов

**Настройка:**
1. Получите PROXY_API_URL у администратора
2. Получите PROXY_API_TOKEN у администратора
3. Скопируйте `config/proxy_api.env.example` → `config/proxy_api.env`
4. Заполните полученными данными
5. Выберите режим "через Proxy API" в GUI

**Тестирование:**
```bash
python scripts/test_proxy_connection.py
```

## 🚀 Быстрый старт с Proxy API

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Настройка proxy
cp config/proxy_api.env.example config/proxy_api.env
# Отредактируйте config/proxy_api.env

# 3. Тест подключения
python scripts/test_proxy_connection.py

# 4. Запуск GUI
python run_gui.py
# Выберите "Удаленная БД (через Proxy API)"
```
```

---

## ✅ ЧЕКЛИСТ ИНТЕГРАЦИИ

### Шаг 1: Подготовка (после деплоя Proxy API)
- [ ] Получить PROXY_API_URL от Railway.com
- [ ] Получить или сгенерировать PROXY_API_TOKEN
- [ ] Убедиться что Proxy API работает (открыть /api/health в браузере)

### Шаг 2: Создание файлов
- [ ] Создать `src/proxy_db_connector.py`
- [ ] Создать `config/proxy_api.env.example`
- [ ] Создать `config/proxy_api.env` с реальными данными
- [ ] Создать `scripts/test_proxy_connection.py`
- [ ] Обновить `requirements.txt` (добавить requests)
- [ ] Обновить `.gitignore` (добавить proxy_api.env)

### Шаг 3: Обновление существующего кода
- [ ] Обновить `src/gui_app.py` - добавить выбор режима подключения
- [ ] Обновить `docs/README.md` - описать новый режим

### Шаг 4: Тестирование
- [ ] Установить зависимости: `pip install requests urllib3`
- [ ] Запустить тест: `python scripts/test_proxy_connection.py`
- [ ] Убедиться что все 6 тестов проходят успешно
- [ ] Запустить GUI и протестировать с Proxy режимом
- [ ] Выполнить реальный анализ продаж через Proxy

### Шаг 5: Документация
- [ ] Создать инструкцию для пользователей
- [ ] Описать процесс получения токена
- [ ] Добавить troubleshooting секцию

### Шаг 6: Распространение
- [ ] Раздать PROXY_API_TOKEN доверенным пользователям
- [ ] Обучить пользователей настройке
- [ ] Создать пример config файла для пользователей

---

## 🔍 TROUBLESHOOTING

### Ошибка: "PROXY_API_URL не настроен"
**Решение:**
1. Проверьте наличие файла `config/proxy_api.env`
2. Убедитесь что в файле есть строка: `PROXY_API_URL=...`
3. Проверьте что `.env` файл загружается в коде

### Ошибка: "Ошибка аутентификации: неверный API токен"
**Решение:**
1. Проверьте PROXY_API_TOKEN в `config/proxy_api.env`
2. Убедитесь что токен соответствует настройкам на Railway
3. Проверьте что нет лишних пробелов в токене

### Ошибка: "Не удается подключиться к Proxy API"
**Решение:**
1. Проверьте доступность: откройте `{PROXY_API_URL}/api/health` в браузере
2. Убедитесь что у вас есть интернет
3. Проверьте что URL правильный (с https://)
4. Проверьте firewall настройки

### Ошибка: "Превышен лимит запросов"
**Решение:**
1. Подождите 1 минуту
2. Если проблема повторяется - обратитесь к администратору для увеличения лимита

---

## 📊 Сравнение режимов подключения

| Параметр | Локальная БД | Удаленная (прямая) | Удаленная (Proxy) |
|----------|--------------|-------------------|-------------------|
| Требует whitelist | ❌ | ✅ | ❌ |
| Работает с любого IP | ✅ | ❌ | ✅ |
| Скорость | 🔥🔥🔥 | 🔥🔥 | 🔥 |
| Безопасность | 🔒 | 🔒🔒 | 🔒🔒🔒 |
| Аудит запросов | ❌ | ❌ | ✅ |
| Настройка | Легко | Средне | Легко |
| Для production | ❌ | ⚠️ | ✅ |

---

**Дата создания:** 2025-10-17  
**Автор:** Senior Developer  
**Статус:** Готов к интеграции 🚀






