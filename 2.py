# ==============================
# 📊 STOCK PATTERN DETECTION DASHBOARD
# Tech: Python + Streamlit + yfinance
# ==============================

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ==============================
# 🔹 USER INPUT
# ==============================

st.title("📈 TradingView-like Pattern Detection Dashboard")

ticker = st.text_input("Enter Stock (e.g. RELIANCE.NS)", "RELIANCE.NS")
interval = st.selectbox("Select Timeframe", ["1m", "5m", "15m", "1h"])
period = st.selectbox("Select Period", ["1d", "5d", "1mo"])

# ==============================
# 🔹 FETCH DATA
# ==============================

@st.cache_data
def load_data(ticker, interval, period):
    data = yf.download(ticker, interval=interval, period=period)
    data.dropna(inplace=True)
    return data

if st.button("Load Data"):
    data = load_data(ticker, interval, period)

    st.subheader("Raw Data")
    st.write(data.tail())

    # ==============================
    # 🔹 PATTERN LOGIC
    # ==============================

    # 1. Breakout Detection
    data['Resistance'] = data['High'].rolling(20).max()
    data['Breakout'] = data['Close'] > data['Resistance']

    # 2. Support Breakdown
    data['Support'] = data['Low'].rolling(20).min()
    data['Breakdown'] = data['Close'] < data['Support']

    # 3. Simple Double Top Detection
    data['Peak'] = (data['High'] > data['High'].shift(1)) & (data['High'] > data['High'].shift(-1))

    peaks = data[data['Peak']]

    double_top_idx = []
    for i in range(1, len(peaks)):
        if abs(peaks['High'].iloc[i] - peaks['High'].iloc[i-1]) < 2:
            double_top_idx.append(peaks.index[i])

    data['DoubleTop'] = data.index.isin(double_top_idx)

    # ==============================
    # 🔹 CHART (PLOTLY)
    # ==============================

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candles"
    ))

    # Breakout markers
    breakout_points = data[data['Breakout']]
    fig.add_trace(go.Scatter(
        x=breakout_points.index,
        y=breakout_points['Close'],
        mode='markers',
        name='Breakout',
        marker=dict(size=10, symbol='triangle-up')
    ))

    # Breakdown markers
    breakdown_points = data[data['Breakdown']]
    fig.add_trace(go.Scatter(
        x=breakdown_points.index,
        y=breakdown_points['Close'],
        mode='markers',
        name='Breakdown',
        marker=dict(size=10, symbol='triangle-down')
    ))

    # Double Top markers
    dt_points = data[data['DoubleTop']]
    fig.add_trace(go.Scatter(
        x=dt_points.index,
        y=dt_points['High'],
        mode='markers',
        name='Double Top',
        marker=dict(size=12, symbol='x')
    ))

    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 🔹 SIGNAL SUMMARY
    # ==============================

    st.subheader("📊 Signals Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Breakouts", int(data['Breakout'].sum()))
    col2.metric("Breakdowns", int(data['Breakdown'].sum()))
    col3.metric("Double Tops", int(data['DoubleTop'].sum()))

# ==============================
# 🚀 RUN COMMAND
# streamlit run filename.py
# ==============================
