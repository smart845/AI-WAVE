# SCALP AI — My Scalper

Готовое клиент-сайд приложение для интрадей/скальпинга:
- Binance REST + WebSocket (1m/3m/5m/15m/1h)
- Свечи + объём, EMA(9/21/50), VWAP, RSI(14)
- Watchlist, сигнальные попапы, настройки (Telegram token)
- Управление графиком: Zoom/Scroll/Reset/Realtime + хоткеи (+/-, ←/→, R, End)

## Локально
```bash
npm i
npm run dev
```

## Vercel
- Import GitHub Repo
- Build: `npm run build`
- Output: `dist`

Все ключи хранятся в localStorage. Сервер не требуется.
