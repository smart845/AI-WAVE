import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import requests
import time
import json
from datetime import datetime
import numpy as np

# === CONFIG ===
st.set_page_config(
    page_title="🚀 AI Wave Trader Pro",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🐸"
)

# === СТИЛИ ===
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #FF4B4B, #FF8C42, #FFD166, #06D6A0, #118AB2, #073B4C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #06D6A0;
    }
    .signal-buy {
        background: rgba(0,255,0,0.2) !important;
        border-left: 4px solid #00FF00 !important;
    }
    .signal-sell {
        background: rgba(255,0,0,0.2) !important;
        border-left: 4px solid #FF0000 !important;
    }
</style>
""", unsafe_allow_html=True)

# === ЗАГОЛОВОК ===
st.markdown('<h1 class="main-header">🚀 AI Wave Trader Pro</h1>', unsafe_allow_html=True)
st.markdown("### 🤖 Умный торговый анализ на основе волн Эллиотта и ИИ")

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/frog.png", width=80)
    st.markdown("### ⚙️ Настройки")
    
    # Выбор пары
    symbol = st.selectbox(
        "🎯 Торговая пара",
        ["SOLUSDT", "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "AVAXUSDT"],
        index=0
    )
    
    # Таймфрейм
    tf = st.selectbox(
        "⏰ Таймфрейм",
        ["1m", "3m", "5m", "15m", "1h", "4h"],
        index=2
    )
    
    # Выбор ИИ
    ai_provider = st.selectbox(
        "🧠 ИИ-аналитик", 
        ["DeepSeek AI", "GPT-4 Simulation", "Claude Simulation", "Local AI"],
        index=0
    )
    
    # Параметры анализа
    st.markdown("### 📊 Параметры анализа")
    rsi_period = st.slider("RSI Период", 5, 30, 14)
    wave_sensitivity = st.slider("Чувствительность волн", 1, 10, 5)
    
    # Кнопки управления
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Старт", type="primary", use_container_width=True)
    with col2:
        stop_btn = st.button("⏹️ Стоп", use_container_width=True)

# === ФУНКЦИИ ДЛЯ ДАННЫХ ===
@st.cache_data(ttl=60)
def get_binance_klines(_symbol, _tf, limit=200):
    """Получение данных с Binance API (публичный доступ)"""
    try:
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': _symbol,
            'interval': _tf,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        return df
    except Exception as e:
        st.error(f"Ошибка получения данных: {e}")
        return None

def calculate_indicators(df):
    """Расчет технических индикаторов"""
    if df is None or df.empty:
        return df
    
    # RSI
    df['rsi'] = ta.rsi(df['close'], length=rsi_period)
    
    # MACD
    macd = ta.macd(df['close'])
    df['macd'] = macd['MACD_12_26_9']
    df['macd_signal'] = macd['MACDs_12_26_9']
    df['macd_histogram'] = macd['MACDh_12_26_9']
    
    # EMA
    df['ema_20'] = ta.ema(df['close'], length=20)
    df['ema_50'] = ta.ema(df['close'], length=50)
    
    # Волны (упрощенная логика)
    df = detect_elliott_waves(df)
    
    return df

def detect_elliott_waves(df):
    """Упрощенное определение волн Эллиотта"""
    # Ищем локальные максимумы и минимумы
    df['high_peak'] = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))
    df['low_peak'] = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
    
    # Простая логика для демонстрации
    waves = []
    for i in range(len(df)):
        if df['high_peak'].iloc[i]:
            waves.append('Импульсная волна')
        elif df['low_peak'].iloc[i]:
            waves.append('Коррекционная волна')
        else:
            waves.append(None)
    
    df['wave_type'] = waves
    return df

def generate_ai_signal(df, provider):
    """Генерация ИИ-сигнала"""
    if df is None or len(df) < 50:
        return "Недостаточно данных для анализа", "HOLD"
    
    current_price = df['close'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    macd = df['macd'].iloc[-1]
    macd_signal = df['macd_signal'].iloc[-1]
    
    # Анализ тренда
    trend = "Боковой"
    if df['close'].iloc[-1] > df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1]:
        trend = "Восходящий"
    elif df['close'].iloc[-1] < df['ema_20'].iloc[-1] < df['ema_50'].iloc[-1]:
        trend = "Нисходящий"
    
    # Генерация сигнала
    if rsi < 30 and macd > macd_signal:
        signal = "BUY"
        confidence = "Высокая"
        reason = "Перепроданность + бычий дивергенция MACD"
    elif rsi > 70 and macd < macd_signal:
        signal = "SELL" 
        confidence = "Высокая"
        reason = "Перекупленность + медвежий дивергенция MACD"
    else:
        signal = "HOLD"
        confidence = "Средняя"
        reason = "Ожидание четкого сигнала"
    
    analysis = f"""
🧠 **Анализ {provider}:**
- 📈 **Сигнал:** {signal}
- 🎯 **Уверенность:** {confidence} 
- 💰 **Текущая цена:** ${current_price:.2f}
- 📊 **RSI:** {rsi:.1f} ({'Перепроданность' if rsi < 30 else 'Перекупленность' if rsi > 70 else 'Нейтральный'})
- 🔄 **Тренд:** {trend}
- 📝 **Обоснование:** {reason}

💡 **Рекомендация:** {'Рассмотреть покупку' if signal == 'BUY' else 'Рассмотреть продажу' if signal == 'SELL' else 'Ожидать лучшей точки входа'}
"""
    return analysis, signal

def create_advanced_chart(df, signal):
    """Создание продвинутого графика"""
    fig = go.Figure()
    
    # Свечи
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price"
    ))
    
    # EMA
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ema_20'],
        line=dict(color='orange', width=1),
        name="EMA 20"
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['ema_50'],
        line=dict(color='red', width=1),
        name="EMA 50"
    ))
    
    # Разметка волн
    wave_points = df[df['wave_type'].notnull()]
    for idx, row in wave_points.iterrows():
        if row['wave_type'] == 'Импульсная волна':
            fig.add_annotation(
                x=row['timestamp'], y=row['high'],
                text="📈", showarrow=False,
                font=dict(size=16)
            )
        else:
            fig.add_annotation(
                x=row['timestamp'], y=row['low'],
                text="📉", showarrow=False,
                font=dict(size=16)
            )
    
    fig.update_layout(
        title=f"🎯 {symbol} - Волновой анализ Эллиотта",
        xaxis_title="Время",
        yaxis_title="Цена (USDT)",
        height=600,
        showlegend=True,
        template="plotly_dark"
    )
    
    return fig

# === ОСНОВНОЙ ИНТЕРФЕЙС ===

# Инициализация состояния
if 'running' not in st.session_state:
    st.session_state.running = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Обработка кнопок
if start_btn:
    st.session_state.running = True
    st.success("🚀 Анализ запущен!")

if stop_btn:
    st.session_state.running = False
    st.info("⏹️ Анализ остановлен")

# Главные метрики
col1, col2, col3, col4 = st.columns(4)

if st.session_state.running:
    # Получение и обработка данных
    with st.spinner("🔄 Получение данных..."):
        df = get_binance_klines(symbol, tf)
    
    if df is not None and not df.empty:
        df = calculate_indicators(df)
        
        # Обновление метрик
        current_price = df['close'].iloc[-1]
        price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
        rsi_current = df['rsi'].iloc[-1]
        volume = df['volume'].iloc[-1]
        
        with col1:
            st.metric(
                label="💰 Текущая цена",
                value=f"${current_price:.2f}",
                delta=f"{price_change:.2f}%"
            )
        
        with col2:
            st.metric(
                label="📊 RSI",
                value=f"{rsi_current:.1f}",
                delta="Перепроданность" if rsi_current < 30 else "Перекупленность" if rsi_current > 70 else "Нейтральный"
            )
        
        with col3:
            st.metric(
                label="📈 Объем",
                value=f"{volume:.0f}",
                delta="Высокий" if volume > df['volume'].mean() else "Низкий"
            )
        
        with col4:
            ema_trend = "🟢 Бычий" if df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1] else "🔴 Медвежий"
            st.metric(
                label="🎯 Тренд EMA",
                value=ema_trend
            )
        
        # Генерация сигнала
        ai_analysis, signal = generate_ai_signal(df, ai_provider)
        
        # Отображение сигнала
        signal_class = "signal-buy" if signal == "BUY" else "signal-sell" if signal == "SELL" else ""
        st.markdown(f'<div class="metric-card {signal_class}">{ai_analysis}</div>', unsafe_allow_html=True)
        
        # График и дополнительные индикаторы
        chart_col, indicator_col = st.columns([3, 1])
        
        with chart_col:
            fig = create_advanced_chart(df, signal)
            st.plotly_chart(fig, use_container_width=True)
        
        with indicator_col:
            st.markdown("### 📊 Индикаторы")
            
            # Гистограмма MACD
            macd_fig = go.Figure()
            colors = ['green' if x >= 0 else 'red' for x in df['macd_histogram'].tail(20)]
            macd_fig.add_trace(go.Bar(
                x=df['timestamp'].tail(20),
                y=df['macd_histogram'].tail(20),
                marker_color=colors,
                name="MACD Histogram"
            ))
            macd_fig.update_layout(
                title="MACD Гистограмма",
                height=200,
                showlegend=False
            )
            st.plotly_chart(macd_fig, use_container_width=True)
            
            # RSI
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(
                x=df['timestamp'].tail(50),
                y=df['rsi'].tail(50),
                line=dict(color='purple', width=2),
                name="RSI"
            ))
            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
            rsi_fig.update_layout(
                title="RSI",
                height=200,
                yaxis_range=[0, 100],
                showlegend=False
            )
            st.plotly_chart(rsi_fig, use_container_width=True)
        
        # Автоматическое обновление
        st.session_state.last_update = datetime.now()
        time.sleep(2)  # Задержка перед следующим обновлением
        st.rerun()
    else:
        st.warning("Данные не получены. Попробуйте другой символ или таймфрейм.")
else:
    # Стартовый экран
    st.markdown("""
    ## 🐸 Добро пожаловать в AI Wave Trader Pro!
    
    ### 🚀 Возможности:
    - **📊 Автоматический волновой анализ** по Эллиотту
    - **🧠 ИИ-сигналы** для точных входов
    - **📈 Реальные данные** с Binance
    - **🎯 Профессиональные индикаторы**
    
    ### ⚡ Быстрый старт:
    1. Выбери торговую пару
    2. Настрой таймфрейм
    3. Выбери ИИ-аналитика
    4. Нажми **🚀 Старт**
    
    ### 💡 Совет:
    Начни с SOLUSDT на 5m таймфрейме для тестирования!
    """)
    
    # Демо-график
    st.image("https://via.placeholder.com/800x400/373737/FFFFFF?text=AI+Wave+Trader+Pro", use_column_width=True)

# Футер
st.markdown("---")
st.markdown(
    "🐸 **AI Wave Trader Pro** | 📧 Поддержка: @solana_frogg | " +
    "⚖️ Торгуй ответственно | 🚀 Version 2.0"
)
