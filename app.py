import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
import requests
import time
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
        margin: 10px 0;
    }
    .signal-buy {
        background: rgba(0,255,0,0.2) !important;
        border-left: 4px solid #00FF00 !important;
    }
    .signal-sell {
        background: rgba(255,0,0,0.2) !important;
        border-left: 4px solid #FF0000 !important;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# === ЗАГОЛОВОК ===
st.markdown('<h1 class="main-header">🚀 AI Wave Trader Pro</h1>', unsafe_allow_html=True)
st.markdown("### 🤖 Умный торговый анализ на основе волн Эллиотта и ИИ")

# === ИНИЦИАЛИЗАЦИЯ СЕССИИ ===
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0

# === БОКОВАЯ ПАНЕЛЬ ===
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/frog.png", width=80)
    st.markdown("### ⚙️ Настройки")
    
    # Выбор пары
    symbol = st.selectbox(
        "🎯 Торговая пара",
        ["SOLUSDT", "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "AVAXUSDT", "BNBUSDT"],
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
    analyze_btn = st.button("🔍 Анализировать рынок", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("### 📈 Статистика")
    st.info(f"Анализов выполнено: **{st.session_state.analysis_count}**")

# === ФУНКЦИИ ДЛЯ ДАННЫХ ===
@st.cache_data(ttl=30)  # Кэшируем на 30 секунд
def get_binance_klines(_symbol, _tf, limit=100):
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
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        df[numeric_cols] = df[numeric_cols].astype(float)
        
        return df
    except Exception as e:
        st.error(f"Ошибка получения данных: {e}")
        return None

def calculate_indicators(df):
    """Расчет технических индикаторов"""
    if df is None or len(df) < 20:
        return df
    
    try:
        # RSI
        df['rsi'] = ta.rsi(df['close'], length=rsi_period)
        
        # MACD
        macd = ta.macd(df['close'])
        if macd is not None:
            df['macd'] = macd['MACD_12_26_9']
            df['macd_signal'] = macd['MACDs_12_26_9']
            df['macd_histogram'] = macd['MACDh_12_26_9']
        
        # EMA
        df['ema_20'] = ta.ema(df['close'], length=20)
        df['ema_50'] = ta.ema(df['close'], length=50)
        
        # Bollinger Bands
        bollinger = ta.bbands(df['close'], length=20)
        if bollinger is not None:
            df['bb_upper'] = bollinger['BBU_20_2.0']
            df['bb_middle'] = bollinger['BBM_20_2.0']
            df['bb_lower'] = bollinger['BBL_20_2.0']
        
        # Волновой анализ
        df = detect_elliott_waves(df)
        
        return df
    except Exception as e:
        st.error(f"Ошибка расчета индикаторов: {e}")
        return df

def detect_elliott_waves(df):
    """Упрощенное определение волн Эллиотта"""
    try:
        # Ищем локальные максимумы и минимумы
        df['high_peak'] = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))
        df['low_peak'] = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
        
        # Определяем волны
        waves = []
        for i in range(len(df)):
            if df['high_peak'].iloc[i] if i < len(df) else False:
                waves.append('📈 Импульс')
            elif df['low_peak'].iloc[i] if i < len(df) else False:
                waves.append('📉 Коррекция')
            else:
                waves.append(None)
        
        df['wave_type'] = waves
        
        # Определяем текущую волну
        last_20 = df.tail(20)
        high_peaks = last_20[last_20['high_peak'] == True]
        low_peaks = last_20[last_20['low_peak'] == True]
        
        if len(high_peaks) > len(low_peaks):
            current_wave = "Волна 3 (импульсная)"
        elif len(low_peaks) > len(high_peaks):
            current_wave = "Волна 4 (коррекционная)"
        else:
            current_wave = "Волна 2/5 (неопределенность)"
            
        df['current_wave'] = current_wave
        return df
        
    except Exception as e:
        st.error(f"Ошибка волнового анализа: {e}")
        return df

def generate_ai_signal(df, provider):
    """Генерация ИИ-сигнала"""
    if df is None or len(df) < 50:
        return "Недостаточно данных для анализа", "HOLD"
    
    try:
        current_price = df['close'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        
        # Анализ тренда
        trend = "Боковой"
        if len(df) >= 50:
            if df['close'].iloc[-1] > df['ema_20'].iloc[-1] > df['ema_50'].iloc[-1]:
                trend = "🟢 Восходящий"
            elif df['close'].iloc[-1] < df['ema_20'].iloc[-1] < df['ema_50'].iloc[-1]:
                trend = "🔴 Нисходящий"

        # Анализ волатильности
        volatility = df['close'].pct_change().std() * 100
        
        # Генерация сигнала на основе множества факторов
        buy_signals = 0
        sell_signals = 0
        
        if rsi < 35:
            buy_signals += 2
        elif rsi > 65:
            sell_signals += 2
            
        if 'macd' in df.columns and 'macd_signal' in df.columns:
            if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
                buy_signals += 1
            else:
                sell_signals += 1
                
        if trend == "🟢 Восходящий":
            buy_signals += 1
        elif trend == "🔴 Нисходящий":
            sell_signals += 1

        # Формирование итогового сигнала
        if buy_signals >= 3 and sell_signals <= 1:
            signal = "BUY"
            confidence = "Высокая"
            reason = "Сильное бычье схождение индикаторов"
            emoji = "🚀"
        elif sell_signals >= 3 and buy_signals <= 1:
            signal = "SELL"
            confidence = "Высокая"
            reason = "Сильное медвежье схождение индикаторов"
            emoji = "🔻"
        else:
            signal = "HOLD"
            confidence = "Средняя"
            reason = "Ожидание четкого сигнала"
            emoji = "⚡"

        analysis = f"""
{emoji} **Анализ {provider}:**

🎯 **Сигнал:** **{signal}** 
📊 **Уверенность:** {confidence}
💰 **Текущая цена:** ${current_price:.2f}

📈 **Тех. индикаторы:**
- RSI: {rsi:.1f} ({'📉 Перепроданность' if rsi < 30 else '📈 Перекупленность' if rsi > 70 else '↔️ Нейтральный'})
- Тренд: {trend}
- Волатильность: {volatility:.2f}%

💡 **Рекомендация:** {'Рассмотреть покупку' if signal == 'BUY' else 'Рассмотреть продажу' if signal == 'SELL' else 'Ожидать лучшей точки входа'}

📝 **Обоснование:** {reason}
"""
        return analysis, signal
        
    except Exception as e:
        return f"Ошибка анализа: {e}", "HOLD"

def create_advanced_chart(df, signal):
    """Создание продвинутого графика"""
    try:
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
            line=dict(color='orange', width=1.5),
            name="EMA 20"
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['ema_50'],
            line=dict(color='red', width=1.5),
            name="EMA 50"
        ))
        
        # Bollinger Bands
        if 'bb_upper' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['bb_upper'],
                line=dict(color='gray', width=1, dash='dash'),
                name="BB Upper"
            ))
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['bb_lower'],
                line=dict(color='gray', width=1, dash='dash'),
                name="BB Lower",
                fill='tonexty'
            ))
        
        # Разметка волн
        wave_points = df[df['wave_type'].notnull()].tail(10)
        for idx, row in wave_points.iterrows():
            if 'Импульс' in str(row['wave_type']):
                fig.add_annotation(
                    x=row['timestamp'], y=row['high'],
                    text="📈", showarrow=False,
                    font=dict(size=14)
                )
            elif 'Коррекция' in str(row['wave_type']):
                fig.add_annotation(
                    x=row['timestamp'], y=row['low'],
                    text="📉", showarrow=False,
                    font=dict(size=14)
                )
        
        fig.update_layout(
            title=f"🎯 {symbol} | {tf} | Волновой анализ Эллиотта",
            xaxis_title="Время",
            yaxis_title="Цена (USDT)",
            height=600,
            showlegend=True,
            template="plotly_dark"
        )
        
        return fig
    except Exception as e:
        st.error(f"Ошибка создания графика: {e}")
        return go.Figure()

# === ОСНОВНОЙ ИНТЕРФЕЙС ===

# Главные метрики
col1, col2, col3, col4 = st.columns(4)

if analyze_btn or st.session_state.data is not None:
    # Получение и обработка данных
    with st.spinner("🔄 Получение рыночных данных..."):
        df = get_binance_klines(symbol, tf)
    
    if df is not None:
        with st.spinner("📊 Расчет индикаторов..."):
            df = calculate_indicators(df)
            st.session_state.data = df
            st.session_state.analysis_count += 1
            st.session_state.last_update = datetime.now()
        
        # Обновление метрик
        current_price = df['close'].iloc[-1]
        price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
        rsi_current = df['rsi'].iloc[-1] if 'rsi' in df.columns else 50
        volume = df['volume'].iloc[-1]
        
        with col1:
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric(
                label="💰 Текущая цена",
                value=f"${current_price:.4f}" if current_price < 1 else f"${current_price:.2f}",
                delta=f"{price_change:+.2f}%",
                delta_color=delta_color
            )
        
        with col2:
            rsi_status = "📉 Перепроданность" if rsi_current < 30 else "📈 Перекупленность" if rsi_current > 70 else "↔️ Нейтральный"
            st.metric(
                label="📊 RSI",
                value=f"{rsi_current:.1f}",
                delta=rsi_status
            )
        
        with col3:
            avg_volume = df['volume'].tail(20).mean()
            volume_ratio = (volume / avg_volume - 1) * 100
            st.metric(
                label="📈 Объем",
                value=f"{volume:,.0f}",
                delta=f"{volume_ratio:+.1f}% vs ср."
            )
        
        with col4:
            if 'current_wave' in df.columns:
                wave_emoji = "📈" if "импульс" in str(df['current_wave'].iloc[-1]).lower() else "📉"
                st.metric(
                    label="🎯 Текущая волна",
                    value=f"{wave_emoji} {df['current_wave'].iloc[-1]}"
                )
            else:
                st.metric(label="🎯 Тренд", value="Анализ...")
        
        # Генерация сигнала
        with st.spinner("🧠 ИИ анализирует рынок..."):
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
            st.markdown("### 📊 Осцилляторы")
            
            # RSI индикатор
            rsi_fig = go.Figure()
            rsi_fig.add_trace(go.Scatter(
                x=df['timestamp'].tail(50),
                y=df['rsi'].tail(50),
                line=dict(color='purple', width=3),
                name="RSI"
            ))
            rsi_fig.add_hrect(y0=70, y1=100, line_width=0, fillcolor="red", opacity=0.2)
            rsi_fig.add_hrect(y0=30, y1=70, line_width=0, fillcolor="gray", opacity=0.2)
            rsi_fig.add_hrect(y0=0, y1=30, line_width=0, fillcolor="green", opacity=0.2)
            rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
            rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
            rsi_fig.update_layout(
                title="RSI Oscillator",
                height=200,
                yaxis_range=[0, 100],
                showlegend=False,
                margin=dict(t=30, b=0, l=0, r=0)
            )
            st.plotly_chart(rsi_fig, use_container_width=True)
            
            # MACD индикатор
            if 'macd' in df.columns:
                macd_fig = go.Figure()
                colors = ['green' if x >= 0 else 'red' for x in df['macd_histogram'].tail(50)]
                macd_fig.add_trace(go.Bar(
                    x=df['timestamp'].tail(50),
                    y=df['macd_histogram'].tail(50),
                    marker_color=colors,
                    name="MACD Histogram"
                ))
                macd_fig.add_trace(go.Scatter(
                    x=df['timestamp'].tail(50),
                    y=df['macd'].tail(50),
                    line=dict(color='blue', width=2),
                    name="MACD"
                ))
                macd_fig.add_trace(go.Scatter(
                    x=df['timestamp'].tail(50),
                    y=df['macd_signal'].tail(50),
                    line=dict(color='orange', width=2),
                    name="Signal"
                ))
                macd_fig.update_layout(
                    title="MACD",
                    height=200,
                    showlegend=False,
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(macd_fig, use_container_width=True)
        
        # Информация о последнем обновлении
        if st.session_state.last_update:
            st.caption(f"🕐 Последнее обновление: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # Кнопка для повторного анализа
        if st.button("🔄 Обновить анализ", use_container_width=True):
            st.rerun()
    
else:
    st.error("❌ Не удалось получить данные. Проверьте подключение к интернету.")

# Стартовый экран
if st.session_state.data is None and not analyze_btn:
    st.markdown("""
    ## 🐸 Добро пожаловать в AI Wave Trader Pro!
    
    ### 🚀 Возможности:
    - **📊 Автоматический волновой анализ** по Эллиотту
    - **🧠 ИИ-сигналы** для точных входов
    - **📈 Реальные данные** с Binance API
    - **🎯 Профессиональные индикаторы** (RSI, MACD, EMA, Bollinger Bands)
    
    ### ⚡ Быстрый старт:
    1. Выбери торговую пару в боковой панели
    2. Настрой таймфрейм анализа
    3. Выбери ИИ-аналитика
    4. Нажми **🔍 Анализировать рынок**
    
    ### 💡 Рекомендации:
    - Начни с **SOLUSDT** на **5m** для тестирования
    - **RSI < 30** - возможна покупка
    - **RSI > 70** - возможна продажа
    - Следи за сходимостью индикаторов
    """)
    
    # Демо-скриншот или placeholder
    st.image("https://via.placeholder.com/800x400/1E1E1E/FFFFFF?text=AI+Wave+Trader+Pro+🚀", use_column_width=True)

# Футер
st.markdown("---")
st.markdown(
    "🐸 **AI Wave Trader Pro v2.0** | "
    "📧 **Поддержка:** @solana_frogg | " 
    "⚖️ **Торгуй ответственно** | "
    "🔒 **100% безопасно** (без приватных ключей)"
)