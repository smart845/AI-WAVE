# 🚀 AI Wave Trader Pro

Streamlit-приложение для визуального и технического анализа (RSI, MACD, EMA) + упрощённые волны Эллиотта.

## 🔧 Локальный запуск
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 🌐 Деплой
### A) Streamlit Community Cloud (просто)
1) Залей проект в GitHub (минимум `app.py`, `requirements.txt`).
2) Подключи репозиторий на https://share.streamlit.io

### B) Vercel (экспериментально)
Vercel не поддерживает Streamlit напрямую. Добавлены `server.py` и `vercel.json` для обхода — запускается подпроцесс Streamlit.
> На бесплатных тарифах может быть нестабильно.

