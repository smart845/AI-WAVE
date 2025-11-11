from fastapi import FastAPI
from dash import Dash, html, dcc
import plotly.graph_objects as go
import pandas as pd
import requests

server = FastAPI()
app = Dash(__name__, server=server, routes_pathname_prefix="/")

def get_binance_data(symbol="SOLUSDT", tf="5m", limit=100):
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
    except Exception:
        return pd.DataFrame()

df = get_binance_data()

fig = go.Figure(data=[go.Candlestick(
    x=df["timestamp"],
    open=df["open"], high=df["high"],
    low=df["low"], close=df["close"]
)])
fig.update_layout(template="plotly_dark", title="🎯 SOLUSDT - Binance Demo", height=500)

app.layout = html.Div([
    html.H1("🚀 AI Wave Trader Pro (Render Edition)", style={
        "textAlign":"center",
        "background":"linear-gradient(90deg,#FF4B4B,#FF8C42,#FFD166,#06D6A0,#118AB2,#073B4C)",
        "-webkit-background-clip":"text",
        "-webkit-text-fill-color":"transparent"
    }),
    html.P("🤖 Умный торговый анализ на основе волн Эллиотта и ИИ", style={"textAlign":"center"}),
    dcc.Graph(figure=fig),
    html.Div("🐸 AI Wave Trader Pro | 📧 @solana_frogg | ⚖️ Торгуй ответственно", 
             style={"textAlign":"center","marginTop":"40px","color":"#aaa"})
])

@server.get("/")
def root():
    return {"message": "AI Wave Trader Pro Render edition is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(server, host="0.0.0.0", port=10000)
