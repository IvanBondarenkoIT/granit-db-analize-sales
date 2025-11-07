# 🚀 Railway Deployment Guide

Инструкция по развёртыванию backend (FastAPI прокси) и frontend (Next.js UI) на Railway.

## 📦 Структура

```
web/
├── backend/    # FastAPI прокси для Firebird Proxy API
└── frontend/   # Next.js 14 dashboard
```

Backend и frontend деплоятся как два отдельных сервиса на Railway. Каждый имеет Dockerfile.

---

## 1. Подготовка окружения

### 1.1. Репозиторий

- Ветка: `web-proxy-ui`
- Убедитесь, что все изменения закоммичены и запушены (`main` + `web-proxy-ui`).

### 1.2. Токены Proxy API

На Railway backend хранит секреты, поэтому подготовьте значения:

```
PROXY_API_URL=http://85.114.224.45:8000
PROXY_PRIMARY_TOKEN=<основной токен>
PROXY_FALLBACK_TOKEN=<резервный токен>
SECRET_KEY=<случайная строка 32+ символов>
ALLOWED_ORIGINS=<URL фронтенда Railway, добавим позже>
```

> ⚠️ Никогда не коммитьте реальные токены в git.

---

## 2. Backend (FastAPI)

### 2.1. Локальная проверка

```bash
cd web/backend
cp env.example env
# заполните значения (PROXY_* и SECRET_KEY)

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
# проверить http://127.0.0.1:8001/health
```

### 2.2. Railway сервис

1. Зайти на https://railway.com → New Project → Deploy from GitHub → выбрать репозиторий.
2. Добавить новый сервис: “Dockerfile” → указать путь `web/backend/Dockerfile`.
3. Переменные окружения (Variables):
   - `SECRET_KEY` – случайная строка (`python -c "import secrets; print(secrets.token_hex(32))"`).
   - `PROXY_API_URL`
   - `PROXY_PRIMARY_TOKEN`
   - `PROXY_FALLBACK_TOKEN` (опционально)
   - `PROXY_TIMEOUT=30`
   - `ALLOWED_ORIGINS` – пока можно оставить `http://localhost:3000`, позже заменить на URL фронтенда.
4. После деплоя Railway выдаст URL вида `https://<backend>.up.railway.app` — запишите, он нужен фронтенду.

### 2.3. Настройки

- Порт в Dockerfile — `8001`, Railway автоматом проксирует.
- Логи доступны во вкладке “Logs”.
- Health-check: `GET /health`.

---

## 3. Frontend (Next.js)

### 3.1. Локальная проверка

```bash
cd web/frontend
cp env.example .env.local
# NEXT_PUBLIC_API_BASE_URL = http://127.0.0.1:8001 (или Railway backend URL)

npm install
npm run dev
# http://localhost:3000
```

### 3.2. Railway сервис

1. В том же проекте Railway добавить ещё один сервис: “Dockerfile” → путь `web/frontend/Dockerfile`.
2. Переменные окружения:
   - `NEXT_PUBLIC_API_BASE_URL=https://<backend>.up.railway.app`
3. После билда Railway выдаст URL фронта, например `https://<frontend>.up.railway.app`.
4. Вернитесь в backend → обновите `ALLOWED_ORIGINS` и добавьте URL фронта (`https://<frontend>.up.railway.app`). Перезапустите сервис.

---

## 4. Проверка

1. Откройте фронтенд URL → дашборд должен загрузить данные (карточки и таблица).
2. Убедитесь, что в логах backend нет ошибок авторизации (`401`/`403`).
3. Проверьте health: `https://<backend>.up.railway.app/health`.

---

## 5. Дополнительные советы

- **CI/CD:** подключите автодеплой при пуше в `web-proxy-ui` (Railway → Settings → GitHub Deployments).
- **Monitoring:** можно добавить Sentry или использовать Railway alerts.
- **Авторизация:** пока фронт/бэк открыты. После MVP стоит добавить auth (JWT или basic + middleware).
- **Кэширование:** для частых запросов (например, `/stores`) можно добавить in-memory cache на backend.

---

## 6. Полезные ссылки

- Railway docs: https://docs.railway.app/
- FastAPI: https://fastapi.tiangolo.com/
- Next.js deployment: https://nextjs.org/docs/app/building-your-application/deploying

