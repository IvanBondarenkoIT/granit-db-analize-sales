# Web Proxy UI

Ветка `web-proxy-ui` содержит разработку современного веб-интерфейса для Firebird Proxy API.

## Структура

```
web/
├── backend/   # FastAPI приложение (прокси между браузером и Proxy API)
└── frontend/  # Next.js/Tailwind клиентское приложение
```

### Backend
- `app/main.py` — точка входа FastAPI.
- `app/config.py` — конфигурация (чтение env).
- `app/deps.py` — зависимости (HTTP клиент к Proxy API).
- `app/routers` — маршруты (`/health`, `/stores`, `/sales`).
- `requirements.txt` — зависимости.
- `.env.example` — пример конфигурации (Proxy API URL/токены, secret key).

### Frontend
- Next.js 14 (App Router) + Tailwind CSS.
- React Query для работы с API.
- В переменной `NEXT_PUBLIC_API_BASE_URL` укажите URL backend-прокси (по умолчанию `http://localhost:8001`). Пример файла: `web/frontend/env.example` → скопировать в `.env.local` или `.env`.

## Локальный запуск (backend)

```