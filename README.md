# 🚀 AI Wave Trader Pro — Render v3 (стабильно)

- Без сетевых вызовов на импорте (всё делается при запросе)
- Фиксированы версии Flask/Werkzeug (совместимы с Dash)
- Health-check: GET /health → {"status":"ok"}

## Деплой
Build Command:
    pip install -r requirements.txt
Start Command:
    gunicorn main:server --workers 1 --threads 8 --timeout 120 -b 0.0.0.0:$PORT
Plan: Free

## Локально
pip install -r requirements.txt
python main.py
