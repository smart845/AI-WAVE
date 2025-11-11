# 🚀 AI Wave Trader Pro (Render Edition)

## Быстрый деплой на Render
1) GitHub → репозиторий с файлами из этого архива.
2) https://render.com → New → Web Service → Connect Repository.
3) Если Render не подхватил `render.yaml`, задай вручную:
   - Build Command:
     pip install -r requirements.txt
   - Start Command:
     gunicorn main:server --workers 1 --threads 8 --timeout 120 -b 0.0.0.0:$PORT
4) План: Free, регион любой.

## Локально
pip install -r requirements.txt
python main.py
