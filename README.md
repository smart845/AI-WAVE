# Bybit Sniper Terminal — Stage 1 (Real Public Data)

Это проект под деплой на **Vercel**, который:
- отдаёт `index.html` с твоим интерфейсом;
- имеет backend-прокси `/api/bybit/market/*` для реальных данных Bybit V5 Market;
- фронтенд ходит **только** через этот backend (`CONFIG.bybitAPI = '/api/bybit/market'`).

## Что уже работает на реальных данных

- Tickers (цена, 24h change и т.д.)
- Kline / свечи
- Funding rate (через `funding/history`)
- Open Interest
- Любые другие публичные эндпоинты `/v5/market/*`, которые использует фронт

Все они теперь идут через:
`/api/bybit/market/<endpoint>?<query>`
который проксирует запросы на `https://api.bybit.com/v5/market/<endpoint>?<query>`.

## Локальный запуск (опционально)

```bash
npm install -g vercel
vercel dev
```

Дальше открывай `http://localhost:3000`.

## Деплой на Vercel

1. Создай новый репозиторий на GitHub.
2. Скопируй сюда все файлы из этой папки и сделай `git push`.
3. В Vercel нажми **New Project** → выбери репозиторий.
4. Build Command: можно оставить пустым (по умолчанию Vercel поймёт, что это статический проект с функциями).
5. Output Directory: по умолчанию `.` (корень репозитория).

После деплоя:

- фронтенд будет доступен по адресу проекта;
- все запросы к Bybit будут идти через backend `/api/bybit/market`, что стабильно и CORS-safe.

## Следующие шаги (Stage 2 и далее)

1. Подключить приватные API ключи Bybit на backend и добавить эндпоинты:

   - `/api/trades` — реальные сделки пользователя,
   - `/api/positions` — позиции,
   - `/api/ai-monitor` — агрегированные метрики (win rate, PnL и т.д.).

2. Связать AI Monitor, Smart Sniper и бегущую строку с этими реальными данными.

Сейчас, на этапе 1, всё, что касается публичных рыночных данных (цена, OI, funding, ликвидации и т.п.), идёт с настоящих эндпоинтов Bybit.
