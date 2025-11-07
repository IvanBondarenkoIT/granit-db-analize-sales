# Flask WebApp (Monolith)

Flask-приложение, объединяющее backend и frontend. Работает как веб-интерфейс, который обращается к существующему Firebird Proxy API.

## Структура

```
webapp/
├── app.py             # Точка входа Flask
├── config.py          # Конфигурация (env переменные)
├── proxy_client.py    # Клиент для обращения к Proxy API
├── services/          # Логика агрегирования/форматирования данных
├── templates/         # Jinja2 шаблоны
└── static/            # CSS/JS/изображения
```

## Запуск локально

```bash
cd webapp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env   # заполните значения (SECRET_KEY, PROXY_*).
flask run --host 0.0.0.0 --port 8000

# Либо через python app.py
python app.py
```

По умолчанию приложение будет доступно по адресу http://127.0.0.1:8000.

## Конфигурация
Секреты хранятся в `.env`:

```
SECRET_KEY=...
PROXY_API_URL=http://85.114.224.45:8000
PROXY_PRIMARY_TOKEN=...
PROXY_FALLBACK_TOKEN=...
PROXY_TIMEOUT=30
```

## Deployment

Для деплоя на Railway (или другой хостинг) используется `Dockerfile` и `.dockerignore`. Подробности см. в `docs/RAILWAY_DEPLOYMENT.md` (в разделе Flask варианта).

