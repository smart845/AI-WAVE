from fastapi import FastAPI
from dash import Dash, html, dcc
import plotly.graph_objects as go
import pandas as pd
import requests, os, logging

# ----- FastAPI app -----
server = FastAPI()

# Healthcheck для Render
@server.get("/health")
def health():
    return {"status": "ok"}

# ----- Dash app -----
app = Dash(__name__, server=server, routes_pathname_prefix="/")

def fetch_df(symbol: str = "SOLUSDT", tf: str = "5m", limit: int = 200) -> pd.DataFrame:
    """Загрузка данных с Binance. Никаких сетевых вызовов при импорте!"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": tf, "limit": limit}
        data = requests.get(url, params=params, timeout=10).json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "qav", "trades", "tbbav", "tbqav", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open","high","low","close","volume"]] = df[["open","high","low","close","volume"]].astype(float)
        return df
    except Exception as e:
        logging.exception("Binance fetch failed: %s", e)
        return pd.DataFrame(columns=["timestamp","open","high","low","close","volume"])

def make_figure(symbol: str = "SOLUSDT", tf: str = "5m"):
    df = fetch_df(symbol, tf, 200)
    if df.empty:
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", title="Нет данных (проверьте доступ к сети)", height=500)
        return fig
    fig = go.Figure(data=[go.Candlestick(
        x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"]
    )])
    fig.update_layout(template="plotly_dark", title=f"🎯 {symbol} — {tf} Binance", height=520,
                      xaxis_rangeslider_visible=False)
    return fig

def serve_layout():
    return html.Div([
        html.H1("🚀 AI Wave Trader Pro (Render Edition)", style={
            "textAlign":"center",
            "background":"linear-gradient(90deg,#FF4B4B,#FF8C42,#FFD166,#06D6A0,#118AB2,#073B4C)",
            "-webkit-background-clip":"text",
            "-webkit-text-fill-color":"transparent",
            "margin":"20px 0"
        }),
        html.Div([
            dcc.Dropdown(id="symbol", options=[
                {"label":"SOLUSDT","value":"SOLUSDT"},
                {"label":"BTCUSDT","value":"BTCUSDT"},
                {"label":"ETHUSDT","value":"ETHUSDT"},
                {"label":"ADAUSDT","value":"ADAUSDT"},
            ], value="SOLUSDT", clearable=False, style={"width":"240px","marginRight":"12px"}),
            dcc.Dropdown(id="tf", options=[
                {"label":"1m","value":"1m"},
                {"label":"5m","value":"5m"},
                {"label":"15m","value":"15m"},
                {"label":"1h","value":"1h"},
                {"label":"4h","value":"4h"},
            ], value="5m", clearable=False, style={"width":"120px"}),
        ], style={"display":"flex","justifyContent":"center","gap":"12px"}),
        dcc.Graph(id="chart", figure=make_figure()),
        dcc.Interval(id="tick", interval=60*1000, n_intervals=0),  # автообновление раз в минуту
        html.Div("🐸 AI Wave Trader Pro | 📧 @solana_frogg | ⚖️ Торгуй ответственно",
                 style={"textAlign":"center","marginTop":"24px","color":"#aaa"})
    ])

app.layout = serve_layout

from dash.dependencies import Input, Output

@app.callback(
    Output("chart", "figure"),
    Input("symbol", "value"),
    Input("tf", "value"),
    Input("tick", "n_intervals")
)
def update_chart(symbol, tf, _):
    return make_figure(symbol, tf)

# локальный запуск
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(server, host="0.0.0.0", port=port)
