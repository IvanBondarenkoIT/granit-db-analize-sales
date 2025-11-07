# 🚀 ПРОМПТ ДЛЯ СОЗДАНИЯ НОВОГО ПРОЕКТА: FIREBIRD DATABASE PROXY API

## 📋 Информация о связанном проекте

### Текущий проект (клиент)
**Путь:** `D:\Cursor Projects\Granit DB analize sales`

**Назначение:** GUI приложение для анализа продаж кофе из БД Firebird

**Технологии:**
- Python 3.8+
- fdb (Firebird database driver)
- pandas, matplotlib, seaborn (анализ данных)
- tkinter (GUI)
- python-dotenv (управление конфигурацией)

**Структура:**
```
Granit DB analize sales/
├── src/
│   ├── database_connector.py       # Локальное подключение к БД
│   ├── remote_db_connector.py      # READ-ONLY удаленное подключение
│   ├── gui_app.py                  # GUI приложение
│   ├── coffee_analysis.py          # Логика анализа продаж
│   └── logger_config.py            # Настройка логирования
├── config/
│   └── remote_db.env.example       # Параметры подключения к БД
├── docs/                           # Документация
├── tests/                          # Тесты
├── scripts/                        # Скрипты запуска
├── requirements.txt                # Python зависимости
└── run_gui.py                      # Точка входа GUI
```

**Текущее подключение к БД:**
```python
# Прямое подключение к Firebird серверу
DSN: 85.114.224.45/3055:DK_GEORGIA
User: SYSDBA
Password: masterkey
Charset: UTF8

# Используется алиас БД: DK_GEORGIA
# Реальный путь на сервере: G:\Гранит\GRANITDB\GEORGIA.GDB
```

**Основные операции с БД:**
- SELECT запросы к таблицам: STORGRP, STORZAKAZDT, STORZDTGDS, GOODS
- Расчет сумм продаж, количества чашек кофе, килограммов
- Группировка по магазинам и датам
- Экспорт результатов в Excel

**Проблема:**
- Firebird сервер имеет whitelist IP адресов
- Нужен доступ с множества устройств с разных локаций
- Прямое подключение возможно только с разрешенных IP

---

## 🎯 ЦЕЛЬ НОВОГО ПРОЕКТА

Создать **Database Gateway/Proxy API**, который:

1. **Размещается на Railway.com** (или аналогичной платформе) с фиксированным IP
2. **Имеет один статический IP адрес**, который добавляется в whitelist на Firebird сервере
3. **Предоставляет REST API** для выполнения SELECT запросов к БД
4. **Обеспечивает безопасность** через Bearer Token аутентификацию
5. **Валидирует SQL запросы** - только SELECT, без опасных операций
6. **Логирует все операции** для аудита и отладки
7. **Защищает от перегрузки** через rate limiting

---

## 🏗️ ТРЕБОВАНИЯ К НОВОМУ ПРОЕКТУ

### Название проекта
`firebird-db-proxy` или `granit-db-gateway`

### Директория
**НЕ внутри текущего проекта!** Создать отдельно:
```
D:\Cursor Projects\firebird-db-proxy\
```

### Технологический стек

**Backend Framework:**
- **FastAPI** (рекомендуется) - современный, async, автоматическая документация
- Альтернатива: Flask + Flask-RESTX

**Зависимости:**
```txt
# Web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
fdb==2.0.2

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Rate limiting
slowapi==0.1.9

# Utilities
python-dotenv==1.0.0
pandas==2.1.4

# CORS
python-cors==1.0.0

# Development
pytest==7.4.3
httpx==0.25.2  # для тестирования API
black==23.9.1
flake8==6.1.0
```

### Структура проекта

```
firebird-db-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Настройки (pydantic-settings)
│   ├── auth.py                     # Bearer Token аутентификация
│   ├── database.py                 # Firebird connection pool
│   ├── validators.py               # SQL валидация
│   ├── rate_limiter.py             # Rate limiting logic
│   ├── models.py                   # Pydantic models для API
│   └── routers/
│       ├── __init__.py
│       ├── query.py                # POST /api/query
│       ├── health.py               # GET /api/health
│       └── info.py                 # GET /api/tables, /api/info
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_validators.py
│   ├── test_api.py
│   └── conftest.py
├── docs/
│   ├── API.md                      # API документация
│   ├── DEPLOYMENT.md               # Инструкции по деплою
│   └── SECURITY.md                 # Документация по безопасности
├── scripts/
│   ├── generate_token.py           # Генерация API токенов
│   └── test_connection.py          # Тест подключения к Firebird
├── .env.example                    # Пример environment variables
├── .gitignore
├── requirements.txt
├── Dockerfile                      # Для Railway deployment
├── railway.json                    # Railway конфигурация (опционально)
├── README.md
└── LICENSE
```

---

## 📝 ДЕТАЛЬНЫЕ ТРЕБОВАНИЯ К ФУНКЦИОНАЛЬНОСТИ

### 1. Аутентификация (app/auth.py)

```python
"""
Требования:
- Bearer Token аутентификация
- Токен передается в заголовке: Authorization: Bearer <token>
- Токен хранится в environment variable: API_TOKEN
- Поддержка нескольких токенов (через запятую): API_TOKENS=token1,token2,token3
- Возврат 401 Unauthorized при неверном токене
- Логирование всех попыток доступа
"""

# Пример использования в API:
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    valid_tokens = os.getenv("API_TOKENS", "").split(",")
    
    if token not in valid_tokens:
        logger.warning(f"Invalid token attempt: {token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    return token
```

### 2. Валидация SQL (app/validators.py)

```python
"""
Требования:
- Только SELECT и WITH запросы разрешены
- Блокировать: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE
- Блокировать: EXECUTE BLOCK, EXECUTE PROCEDURE
- Блокировать: множественные запросы через точку с запятой
- Удалять SQL комментарии перед проверкой
- Возвращать детальную ошибку при обнаружении запрещенных операций
- Логировать все заблокированные запросы
"""

import re
from typing import Tuple

FORBIDDEN_PATTERNS = [
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b',
    r'\b(EXECUTE\s+BLOCK)\b',
    r'\b(EXECUTE\s+PROCEDURE)\b',
    r';.*;\s*',  # Множественные запросы
]

def validate_sql(query: str) -> Tuple[bool, str]:
    """
    Валидация SQL запроса.
    
    Returns:
        (is_valid, error_message)
    """
    # Удалить комментарии
    query_clean = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query_clean = re.sub(r'/\*.*?\*/', '', query_clean, flags=re.DOTALL)
    
    # Проверка на запрещенные паттерны
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, query_clean, re.IGNORECASE):
            return False, f"Forbidden operation detected: {pattern}"
    
    # Проверка что это SELECT или WITH
    query_stripped = query_clean.strip().upper()
    if not (query_stripped.startswith('SELECT') or query_stripped.startswith('WITH')):
        return False, "Only SELECT and WITH queries are allowed"
    
    return True, "OK"
```

### 3. Database Connection (app/database.py)

```python
"""
Требования:
- Connection pooling для эффективного использования соединений
- Таймауты подключения и запросов
- Автоматическое переподключение при обрыве связи
- Graceful shutdown при остановке приложения
- Логирование всех операций с БД
"""

import fdb
from contextlib import contextmanager
from typing import Optional
import logging

class FirebirdConnectionPool:
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        max_connections: int = 10,
        connection_timeout: int = 10
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.logger = logging.getLogger(__name__)
        
        self.dsn = f"{host}/{port}:{database}"
        self.logger.info(f"Initialized Firebird pool: {self.dsn}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup"""
        conn = None
        try:
            self.logger.debug(f"Connecting to {self.dsn}")
            conn = fdb.connect(
                dsn=self.dsn,
                user=self.user,
                password=self.password,
                charset='UTF8'
            )
            self.logger.debug("Connection established")
            yield conn
        except fdb.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                self.logger.debug("Connection closed")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> list:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Получить названия колонок
            columns = [desc[0] for desc in cursor.description]
            
            # Получить данные
            rows = cursor.fetchall()
            
            # Преобразовать в список словарей
            results = [dict(zip(columns, row)) for row in rows]
            
            cursor.close()
            return results

# Глобальный экземпляр пула
db_pool: Optional[FirebirdConnectionPool] = None

def get_db_pool() -> FirebirdConnectionPool:
    """Dependency для FastAPI"""
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    return db_pool
```

### 4. API Endpoints (app/routers/)

#### POST /api/query (app/routers/query.py)

```python
"""
Выполнение SELECT запроса к БД

Request:
{
    "query": "SELECT ID, NAME FROM STORGRP WHERE ID = ?",
    "params": [1]  // optional
}

Response (Success):
{
    "success": true,
    "data": [
        {"ID": 1, "NAME": "Магазин 1"}
    ],
    "rows_count": 1,
    "execution_time": 0.234,
    "timestamp": "2025-10-17T12:34:56.789Z"
}

Response (Error):
{
    "success": false,
    "error": "SQL validation failed: UPDATE not allowed",
    "timestamp": "2025-10-17T12:34:56.789Z"
}

Status Codes:
- 200: Success
- 400: Invalid request (SQL validation failed)
- 401: Unauthorized (invalid token)
- 429: Too many requests (rate limit exceeded)
- 500: Internal server error (database error)
"""
```

#### GET /api/health (app/routers/health.py)

```python
"""
Проверка работоспособности API и подключения к БД

Response:
{
    "status": "healthy",
    "database_connected": true,
    "uptime_seconds": 3600,
    "version": "1.0.0",
    "timestamp": "2025-10-17T12:34:56.789Z"
}

Status Codes:
- 200: Healthy
- 503: Service unavailable (database connection failed)
"""
```

#### GET /api/tables (app/routers/info.py)

```python
"""
Получить список таблиц в БД (требует аутентификацию)

Response:
{
    "success": true,
    "tables": ["STORGRP", "STORZAKAZDT", "STORZDTGDS", "GOODS"],
    "count": 4,
    "timestamp": "2025-10-17T12:34:56.789Z"
}
"""
```

#### GET /api/schema/{table_name} (app/routers/info.py)

```python
"""
Получить структуру таблицы (требует аутентификацию)

Response:
{
    "success": true,
    "table": "STORGRP",
    "columns": [
        {"name": "ID", "type": "INTEGER", "nullable": false},
        {"name": "NAME", "type": "VARCHAR(100)", "nullable": true}
    ],
    "timestamp": "2025-10-17T12:34:56.789Z"
}
"""
```

### 5. Rate Limiting (app/rate_limiter.py)

```python
"""
Требования:
- Ограничение запросов по IP адресу
- Настраиваемые лимиты через environment variables:
  - RATE_LIMIT_PER_MINUTE=60 (60 запросов в минуту)
  - RATE_LIMIT_PER_HOUR=1000 (1000 запросов в час)
- Возврат 429 Too Many Requests при превышении
- Header в ответе: X-RateLimit-Remaining, X-RateLimit-Reset
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# В main.py:
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# В endpoint:
@app.post("/api/query")
@limiter.limit("60/minute")  # 60 запросов в минуту
async def execute_query(request: Request, ...):
    ...
```

### 6. Логирование (app/main.py)

```python
"""
Требования:
- Структурированное логирование всех событий
- Уровни логирования: DEBUG, INFO, WARNING, ERROR
- Логировать:
  - Старт/стоп приложения
  - Все входящие запросы (метод, путь, IP, токен)
  - Выполненные SQL запросы (без параметров с чувствительными данными)
  - Ошибки валидации
  - Ошибки БД
  - Rate limit violations
  - Время выполнения каждого запроса

Формат:
[2025-10-17 12:34:56.789] [INFO] [query.py:45] Query executed successfully - 123 rows in 0.234s
"""

import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

---

## 🔐 ENVIRONMENT VARIABLES (.env.example)

```bash
# ==================== DATABASE ====================
# Firebird server connection
DB_HOST=85.114.224.45
DB_PORT=3055
DB_NAME=DK_GEORGIA
DB_USER=SYSDBA
DB_PASSWORD=masterkey

# Connection pool settings
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=10
DB_QUERY_TIMEOUT=30

# ==================== SECURITY ====================
# API Authentication (Bearer Token)
# Можно указать несколько токенов через запятую
API_TOKENS=your-secret-token-1,your-secret-token-2

# CORS settings (для web клиентов)
ALLOWED_ORIGINS=*
# Или конкретные домены:
# ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com

# ==================== RATE LIMITING ====================
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# ==================== LOGGING ====================
LOG_LEVEL=INFO
# Опции: DEBUG, INFO, WARNING, ERROR, CRITICAL

# ==================== APPLICATION ====================
APP_NAME=Firebird DB Proxy
APP_VERSION=1.0.0
APP_ENV=production
# Опции: development, staging, production

# ==================== RAILWAY (автоматически) ====================
# Railway автоматически устанавливает:
# PORT=8000 (порт на котором слушает приложение)
# RAILWAY_STATIC_URL=https://your-app.railway.app
# RAILWAY_ENVIRONMENT=production
```

---

## 🐳 DOCKERFILE

```dockerfile
# Для Railway deployment

FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY ./app ./app

# Порт приложения (Railway установит автоматически)
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 ТЕСТИРОВАНИЕ (tests/)

### test_validators.py
```python
"""
Тесты валидации SQL:
- SELECT запросы разрешены ✅
- WITH CTE запросы разрешены ✅
- INSERT заблокирован ❌
- UPDATE заблокирован ❌
- DELETE заблокирован ❌
- DROP заблокирован ❌
- Множественные запросы заблокированы ❌
- SQL комментарии удаляются корректно ✅
"""

import pytest
from app.validators import validate_sql

def test_select_allowed():
    query = "SELECT * FROM STORGRP"
    is_valid, _ = validate_sql(query)
    assert is_valid == True

def test_update_blocked():
    query = "UPDATE STORGRP SET NAME = 'Test'"
    is_valid, error = validate_sql(query)
    assert is_valid == False
    assert "Forbidden" in error
```

### test_auth.py
```python
"""
Тесты аутентификации:
- Валидный токен ✅
- Невалидный токен ❌
- Отсутствие токена ❌
- Несколько токенов ✅
"""
```

### test_api.py
```python
"""
Интеграционные тесты API:
- POST /api/query с валидным запросом ✅
- POST /api/query с невалидным SQL ❌
- POST /api/query без токена ❌
- GET /api/health ✅
- GET /api/tables с токеном ✅
- Rate limiting работает ✅
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_query_with_valid_token():
    response = client.post(
        "/api/query",
        json={"query": "SELECT 1 FROM RDB$DATABASE"},
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
```

---

## 🚀 DEPLOYMENT НА RAILWAY.COM

### Шаг 1: Подготовка проекта
```bash
# Инициализация Git репозитория
cd firebird-db-proxy
git init
git add .
git commit -m "Initial commit: Firebird DB Proxy API"

# Создать репозиторий на GitHub
# Запушить код
git remote add origin https://github.com/your-username/firebird-db-proxy.git
git push -u origin main
```

### Шаг 2: Deploy на Railway
1. Зайти на https://railway.com/
2. Создать новый проект
3. Выбрать "Deploy from GitHub repo"
4. Выбрать репозиторий `firebird-db-proxy`
5. Railway автоматически обнаружит Dockerfile и задеплоит

### Шаг 3: Настройка Environment Variables
В Railway Dashboard → Variables добавить:
```
DB_HOST=85.114.224.45
DB_PORT=3055
DB_NAME=DK_GEORGIA
DB_USER=SYSDBA
DB_PASSWORD=masterkey
API_TOKENS=<сгенерировать сильный токен>
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
LOG_LEVEL=INFO
```

### Шаг 4: Получить статический IP
1. Railway Dashboard → Settings → Networking
2. Enable Static IP
3. Скопировать IP адрес
4. **ВАЖНО:** Добавить этот IP в whitelist на Firebird сервере!

### Шаг 5: Настроить домен (опционально)
1. Railway автоматически предоставляет домен: `your-app.railway.app`
2. Можно подключить свой домен

---

## 📖 README.md

```markdown
# 🔄 Firebird Database Proxy API

Безопасный REST API gateway для доступа к Firebird БД с множества устройств.

## 🎯 Назначение

Proxy API позволяет выполнять READ-ONLY запросы к Firebird БД через HTTP API,
обходя ограничения IP whitelist сервера.

## 🚀 Быстрый старт

### API URL
```
Production: https://your-app.railway.app
```

### Аутентификация
Все запросы требуют Bearer Token:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-app.railway.app/api/health
```

### Выполнение запроса
```bash
curl -X POST https://your-app.railway.app/api/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT ID, NAME FROM STORGRP",
    "params": []
  }'
```

## 📚 Документация

- Swagger UI: https://your-app.railway.app/docs
- ReDoc: https://your-app.railway.app/redoc
- API Docs: [docs/API.md](docs/API.md)

## 🔒 Безопасность

- ✅ Только SELECT запросы
- ✅ Bearer Token аутентификация
- ✅ Rate limiting
- ✅ SQL injection защита
- ✅ HTTPS only

## 📊 Мониторинг

Health check: https://your-app.railway.app/api/health

## 🛠️ Development

См. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
```

---

## ✅ ЧЕКЛИСТ РАЗРАБОТКИ

### Фаза 1: Инициализация
- [ ] Создать директорию проекта
- [ ] Инициализировать Git
- [ ] Создать виртуальное окружение
- [ ] Установить зависимости
- [ ] Создать структуру папок
- [ ] Создать .gitignore и .env.example

### Фаза 2: Разработка Backend
- [ ] Создать app/config.py (pydantic settings)
- [ ] Реализовать app/auth.py (Bearer Token)
- [ ] Реализовать app/validators.py (SQL validation)
- [ ] Реализовать app/database.py (connection pool)
- [ ] Создать app/models.py (Pydantic models)
- [ ] Реализовать app/routers/query.py (POST /api/query)
- [ ] Реализовать app/routers/health.py (GET /api/health)
- [ ] Реализовать app/routers/info.py (GET /api/tables, etc)
- [ ] Создать app/main.py (FastAPI app initialization)
- [ ] Настроить CORS
- [ ] Настроить rate limiting
- [ ] Настроить логирование

### Фаза 3: Тестирование
- [ ] Написать tests/test_validators.py
- [ ] Написать tests/test_auth.py
- [ ] Написать tests/test_api.py
- [ ] Запустить все тесты локально
- [ ] Тест подключения к реальной БД

### Фаза 4: Документация
- [ ] Создать README.md
- [ ] Создать docs/API.md
- [ ] Создать docs/DEPLOYMENT.md
- [ ] Создать docs/SECURITY.md
- [ ] Обновить комментарии в коде

### Фаза 5: Deployment
- [ ] Создать Dockerfile
- [ ] Протестировать Docker локально
- [ ] Создать GitHub репозиторий
- [ ] Запушить код на GitHub
- [ ] Создать проект на Railway.com
- [ ] Задеплоить на Railway
- [ ] Настроить Environment Variables
- [ ] Получить статический IP
- [ ] Добавить IP в Firebird whitelist
- [ ] Протестировать production API

### Фаза 6: Интеграция с клиентом
- [ ] Создать клиентскую библиотеку (см. CLIENT_INTEGRATION_PROMPT.md)
- [ ] Обновить текущий проект
- [ ] Протестировать полный workflow
- [ ] Обновить документацию клиента

---

## 🎓 ДОПОЛНИТЕЛЬНЫЕ ИНСТРУКЦИИ

### Приоритеты при разработке:
1. **БЕЗОПАСНОСТЬ** - самое важное!
2. **НАДЕЖНОСТЬ** - обработка всех ошибок
3. **ПРОИЗВОДИТЕЛЬНОСТЬ** - оптимизация запросов
4. **УДОБСТВО** - простота использования API

### Код стиль:
- PEP 8 для Python кода
- Type hints везде где возможно
- Docstrings для всех функций и классов
- Комментарии для сложной логики

### Best Practices:
- Никогда не логировать пароли или токены полностью
- Использовать environment variables для всех секретов
- Graceful shutdown для всех соединений
- Детальные сообщения об ошибках в логах, но не в API responses

---

## 📞 СВЯЗЬ С КЛИЕНТСКИМ ПРОЕКТОМ

После завершения разработки proxy, нужно создать:
1. **proxy_client.py** - библиотека для клиента (см. CLIENT_INTEGRATION_PROMPT.md)
2. Обновить `src/remote_db_connector.py` для использования proxy
3. Обновить документацию в клиентском проекте

---

**Дата создания:** 2025-10-17  
**Автор:** Senior Developer  
**Статус:** Готов к разработке 🚀






