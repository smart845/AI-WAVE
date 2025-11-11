import subprocess, os, time
from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def index():
    # Запуск streamlit как подпроцесса (экспериментально для Vercel)
    cmd = ["streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true", "--browser.gatherUsageStats", "false"]
    subprocess.Popen(cmd)
    time.sleep(1.5)
    return Response('<meta http-equiv="refresh" content="0; url=http://127.0.0.1:8501">', mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
