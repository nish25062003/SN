import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChartScan – Pattern Detection",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0e1a;
    --bg2: #111827;
    --bg3: #1a2235;
    --accent: #00e5ff;
    --accent2: #7c3aed;
    --green: #00e676;
    --red: #ff1744;
    --yellow: #ffd600;
    --text: #e2e8f0;
    --muted: #64748b;
    --border: rgba(0,229,255,0.15);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3, h4 {
    font-family: 'Space Mono', monospace !important;
    letter-spacing: -0.02em;
}

/* Header Banner */
.header-banner {
    background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1525 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.header-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(0,229,255,0.06) 0%, transparent 70%);
    pointer-events: none;
}
.header-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
    margin: 0 0 4px 0;
}
.header-sub {
    color: var(--muted);
    font-size: 0.9rem;
    margin: 0;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Pattern Cards */
.pattern-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
}
.pattern-card:hover {
    border-color: var(--accent);
    background: var(--bg3);
}
.pattern-card.selected {
    border-color: var(--accent);
    background: var(--bg3);
    box-shadow: 0 0 20px rgba(0,229,255,0.1);
}
.pattern-name {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--text);
}
.pattern-type {
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 3px;
}
.pattern-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.badge-bearish { background: rgba(255,23,68,0.15); color: var(--red); }
.badge-bullish { background: rgba(0,230,118,0.15); color: var(--green); }

/* Stock Table */
.stock-row {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    transition: all 0.15s;
}
.stock-row:hover { border-color: var(--accent); background: var(--bg3); }
.stock-symbol {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--accent);
}
.stock-name { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
.stock-change-pos { color: var(--green); font-family: 'Space Mono', monospace; font-size: 0.85rem; }
.stock-change-neg { color: var(--red); font-family: 'Space Mono', monospace; font-size: 0.85rem; }

/* Section Label */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

/* Metric Cards */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 18px;
    flex-wrap: wrap;
}
.metric-box {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 18px;
    flex: 1;
    min-width: 100px;
}
.metric-label { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; }
.metric-value { font-family: 'Space Mono', monospace; font-size: 1.1rem; font-weight: 700; color: var(--text); margin-top: 4px; }
.metric-value.green { color: var(--green); }
.metric-value.red { color: var(--red); }
.metric-value.cyan { color: var(--accent); }

/* Timeframe buttons - override streamlit */
div[data-testid="column"] button {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
    padding: 6px 14px !important;
    width: 100% !important;
    transition: all 0.15s !important;
}
div[data-testid="column"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: var(--bg2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# ─── Data Layer ───────────────────────────────────────────────────────────────

PATTERNS = {
    "Double Top": {
        "type": "bearish",
        "description": "Two consecutive peaks at roughly the same level, signaling a reversal from uptrend to downtrend.",
        "icon": "⛰️",
    },
    "Triple Top": {
        "type": "bearish",
        "description": "Three peaks at similar levels before a downside breakout.",
        "icon": "🏔️",
    },
    "Head & Shoulders": {
        "type": "bearish",
        "description": "Left shoulder, higher head, right shoulder — classic topping pattern.",
        "icon": "👤",
    },
    "Reverse Head & Shoulders": {
        "type": "bullish",
        "description": "Inverse of H&S; signals reversal from downtrend to uptrend.",
        "icon": "🔄",
    },
    "Reverse Double Top": {
        "type": "bullish",
        "description": "Two troughs at similar lows, signaling a shift to an uptrend.",
        "icon": "📈",
    },
    "Reverse Triple Top": {
        "type": "bullish",
        "description": "Three lows at similar price levels before an upside breakout.",
        "icon": "🚀",
    },
}

STOCKS = {
    "Double Top": [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "ltp": 2874.50, "change": -1.42, "confidence": 92},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "ltp": 1623.80, "change": -0.87, "confidence": 88},
        {"symbol": "INFY",     "name": "Infosys Limited",  "ltp": 1456.20, "change": -1.10, "confidence": 85},
        {"symbol": "TCS",      "name": "Tata Consultancy", "ltp": 3812.60, "change": -0.54, "confidence": 79},
        {"symbol": "BAJFINANCE","name": "Bajaj Finance",   "ltp": 7234.10, "change": -2.01, "confidence": 76},
    ],
    "Triple Top": [
        {"symbol": "WIPRO",    "name": "Wipro Limited",    "ltp": 453.30,  "change": -1.88, "confidence": 90},
        {"symbol": "ICICIBANK","name": "ICICI Bank",       "ltp": 1102.45, "change": -0.65, "confidence": 84},
        {"symbol": "AXISBANK", "name": "Axis Bank",        "ltp": 1056.70, "change": -1.22, "confidence": 81},
    ],
    "Head & Shoulders": [
        {"symbol": "TATASTEEL","name": "Tata Steel",       "ltp": 134.80,  "change": -2.30, "confidence": 94},
        {"symbol": "SBIN",     "name": "State Bank of India","ltp": 752.60,"change": -1.05, "confidence": 89},
        {"symbol": "MARUTI",   "name": "Maruti Suzuki",    "ltp": 10854.00,"change": -0.72, "confidence": 83},
        {"symbol": "ONGC",     "name": "ONGC Ltd",         "ltp": 268.90,  "change": -1.60, "confidence": 77},
    ],
    "Reverse Head & Shoulders": [
        {"symbol": "SUNPHARMA","name": "Sun Pharma",       "ltp": 1687.40, "change": +2.10, "confidence": 91},
        {"symbol": "HINDUNILVR","name":"Hindustan Unilever","ltp": 2345.60,"change": +1.30, "confidence": 87},
        {"symbol": "NESTLEIND","name": "Nestle India",     "ltp": 24512.00,"change": +0.88, "confidence": 82},
    ],
    "Reverse Double Top": [
        {"symbol": "KOTAKBANK","name": "Kotak Mahindra Bank","ltp": 1834.50,"change": +1.75,"confidence": 93},
        {"symbol": "LTIM",     "name": "LTIMindtree",      "ltp": 5672.80, "change": +2.40, "confidence": 86},
        {"symbol": "DRREDDY",  "name": "Dr Reddy's Labs",  "ltp": 6230.10, "change": +1.55, "confidence": 80},
    ],
    "Reverse Triple Top": [
        {"symbol": "ASIANPAINT","name":"Asian Paints",     "ltp": 2987.60, "change": +3.10, "confidence": 95},
        {"symbol": "TITAN",    "name": "Titan Company",    "ltp": 3412.80, "change": +2.65, "confidence": 88},
    ],
}

TIMEFRAMES = ["5 Min", "15 Min", "1 Hour", "Daily"]


# ─── Synthetic OHLCV Generator ────────────────────────────────────────────────

def generate_ohlcv(pattern: str, timeframe: str, n: int = 120) -> pd.DataFrame:
    """Generate synthetic OHLCV data that visually resembles the selected pattern."""
    np.random.seed(hash(pattern + timeframe) % (2**31))

    tf_map = {"5 Min": 5, "15 Min": 15, "1 Hour": 60, "Daily": 1440}
    minutes = tf_map.get(timeframe, 5)
    now = datetime.now()
    times = [now - timedelta(minutes=minutes * (n - i)) for i in range(n)]

    base_price = 1000.0
    prices = [base_price]

    # Shape the price series to embed the pattern in the second half
    for i in range(1, n):
        phase = i / n
        drift = 0.0
        if pattern in ("Double Top", "Triple Top", "Head & Shoulders"):
            if phase < 0.35:   drift = +0.6
            elif phase < 0.55: drift = -0.4
            elif phase < 0.70: drift = +0.5
            elif phase < 0.85: drift = -0.5
            else:              drift = -0.8
        elif pattern in ("Reverse Head & Shoulders", "Reverse Double Top", "Reverse Triple Top"):
            if phase < 0.35:   drift = -0.6
            elif phase < 0.55: drift = +0.4
            elif phase < 0.70: drift = -0.5
            elif phase < 0.85: drift = +0.5
            else:              drift = +0.8

        noise = np.random.normal(0, 0.5)
        prices.append(max(prices[-1] * (1 + (drift + noise) / 100), 50))

    closes = np.array(prices)
    highs  = closes * (1 + np.abs(np.random.normal(0, 0.003, n)))
    lows   = closes * (1 - np.abs(np.random.normal(0, 0.003, n)))
    opens  = np.roll(closes, 1)
    opens[0] = closes[0]
    volumes = np.random.randint(50000, 500000, n)

    return pd.DataFrame({"time": times, "open": opens, "high": highs,
                          "low": lows, "close": closes, "volume": volumes})


def build_chart(df: pd.DataFrame, symbol: str, pattern: str, timeframe: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["time"], open=df["open"], high=df["high"],
        low=df["low"], close=df["close"], name="Price",
        increasing_line_color="#00e676", decreasing_line_color="#ff1744",
        increasing_fillcolor="rgba(0,230,118,0.8)",
        decreasing_fillcolor="rgba(255,23,68,0.8)",
    ), row=1, col=1)

    # 20 EMA overlay
    df["ema20"] = df["close"].ewm(span=20).mean()
    fig.add_trace(go.Scatter(x=df["time"], y=df["ema20"], name="EMA 20",
                             line=dict(color="rgba(0,229,255,0.7)", width=1.2),
                             mode="lines"), row=1, col=1)

    # Volume bars
    colors = ["rgba(0,230,118,0.5)" if c >= o else "rgba(255,23,68,0.5)"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume",
                         marker_color=colors, showlegend=False), row=2, col=1)

    # Annotate pattern zone (last 40% of bars)
    n = len(df)
    zone_start = df["time"].iloc[int(n * 0.55)]
    zone_end   = df["time"].iloc[-1]
    zone_high  = df["high"].iloc[int(n * 0.55):].max() * 1.005
    zone_low   = df["low"].iloc[int(n * 0.55):].min() * 0.995
    fig.add_shape(type="rect", x0=zone_start, x1=zone_end,
                  y0=zone_low, y1=zone_high,
                  fillcolor="rgba(0,229,255,0.04)",
                  line=dict(color="rgba(0,229,255,0.3)", width=1, dash="dot"),
                  row=1, col=1)
    fig.add_annotation(x=zone_end, y=zone_high,
                       text=f"  {pattern}", showarrow=False,
                       font=dict(color="#00e5ff", size=11, family="Space Mono"),
                       xanchor="right", row=1, col=1)

    fig.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
        font=dict(color="#e2e8f0", family="DM Sans"),
        title=dict(text=f"<b>{symbol}</b>  ·  {timeframe}",
                   font=dict(color="#00e5ff", size=16, family="Space Mono"),
                   x=0.01),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", x=0, y=1.02,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=520,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
        xaxis2=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
        yaxis2=dict(gridcolor="rgba(255,255,255,0.04)", showgrid=True, zeroline=False),
    )
    return fig


# ─── Session State Init ───────────────────────────────────────────────────────
if "selected_pattern" not in st.session_state:
    st.session_state.selected_pattern = None
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None
if "selected_tf" not in st.session_state:
    st.session_state.selected_tf = "Daily"


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">// Chart Patterns</div>', unsafe_allow_html=True)

    for name, meta in PATTERNS.items():
        badge_cls = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
        badge_txt = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
        stock_count = len(STOCKS.get(name, []))
        selected_cls = "selected" if st.session_state.selected_pattern == name else ""

        st.markdown(f"""
        <div class="pattern-card {selected_cls}">
            <div style="display:flex;justify-content:space-between;align-items:start">
                <div>
                    <div class="pattern-name">{meta['icon']}  {name}</div>
                    <div class="pattern-type">{stock_count} stocks detected</div>
                </div>
                <span class="pattern-badge {badge_cls}">{badge_txt}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Select", key=f"btn_{name}", use_container_width=True):
            st.session_state.selected_pattern = name
            st.session_state.selected_stock = None
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-label">// Market Status</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.78rem; color:#64748b; line-height:1.8">
    🟢 &nbsp;NSE / BSE Live<br>
    🕐 &nbsp;Data refreshed: just now<br>
    📊 &nbsp;Scanning 500+ stocks
    </div>
    """, unsafe_allow_html=True)


# ─── Main Area ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div class="header-title">📡 ChartScan</div>
    <div class="header-sub">Automated Technical Pattern Detection · NSE / BSE</div>
</div>
""", unsafe_allow_html=True)

# ── No pattern selected → show summary grid ──────────────────────────────────
if st.session_state.selected_pattern is None:
    st.markdown('<div class="section-label">// Select a Pattern from the Sidebar to Begin</div>',
                unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, (name, meta) in enumerate(PATTERNS.items()):
        badge_cls = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
        badge_txt = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
        count = len(STOCKS.get(name, []))
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="pattern-card" style="min-height:130px">
                <div style="font-size:2rem;margin-bottom:8px">{meta['icon']}</div>
                <div class="pattern-name">{name}</div>
                <div style="margin:6px 0">
                    <span class="pattern-badge {badge_cls}">{badge_txt}</span>
                </div>
                <div style="font-size:0.78rem;color:#64748b;margin-top:8px">{meta['description']}</div>
                <div style="margin-top:10px;font-family:'Space Mono',monospace;
                            font-size:0.8rem;color:#00e5ff">{count} stocks →</div>
            </div>
            """, unsafe_allow_html=True)

# ── Pattern selected ──────────────────────────────────────────────────────────
else:
    pattern = st.session_state.selected_pattern
    meta    = PATTERNS[pattern]
    stocks  = STOCKS.get(pattern, [])

    # Breadcrumb
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#64748b;margin-bottom:18px;font-family:'Space Mono',monospace">
        HOME &nbsp;›&nbsp; <span style="color:#00e5ff">{pattern.upper()}</span>
        {"&nbsp;›&nbsp; <span style='color:#e2e8f0'>" + st.session_state.selected_stock + "</span>"
         if st.session_state.selected_stock else ""}
    </div>
    """, unsafe_allow_html=True)

    # ── No stock selected → show stock list ──────────────────────────────────
    if st.session_state.selected_stock is None:
        left, right = st.columns([2, 1])

        with left:
            badge_cls = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
            badge_txt = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:20px">
                <span style="font-size:2.2rem">{meta['icon']}</span>
                <div>
                    <div style="font-family:'Space Mono',monospace;font-size:1.3rem;
                                font-weight:700;color:#e2e8f0">{pattern}</div>
                    <span class="pattern-badge {badge_cls}" style="margin-top:4px;display:inline-block">
                        {badge_txt}
                    </span>
                </div>
            </div>
            <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:22px;
                        line-height:1.6;max-width:480px">{meta['description']}</div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-label">// Stocks with Pattern Detected</div>',
                        unsafe_allow_html=True)

            for s in stocks:
                chg_cls  = "stock-change-pos" if s["change"] >= 0 else "stock-change-neg"
                chg_sign = "+" if s["change"] >= 0 else ""
                conf_color = "#00e676" if s["confidence"] >= 90 else \
                             "#ffd600" if s["confidence"] >= 80 else "#ff9100"

                col_info, col_price, col_btn = st.columns([3, 2, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="padding:10px 0">
                        <div class="stock-symbol">{s['symbol']}</div>
                        <div class="stock-name">{s['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_price:
                    st.markdown(f"""
                    <div style="padding:10px 0;text-align:right">
                        <div style="font-family:'Space Mono',monospace;font-size:0.9rem;
                                    color:#e2e8f0">₹{s['ltp']:,.2f}</div>
                        <div class="{chg_cls}">{chg_sign}{s['change']}%</div>
                        <div style="font-size:0.68rem;color:{conf_color};
                                    font-family:'Space Mono',monospace">
                            ⬤ {s['confidence']}% conf
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    if st.button("Analyze →", key=f"stock_{s['symbol']}"):
                        st.session_state.selected_stock = s["symbol"]
                        st.rerun()

                st.markdown('<hr style="border-color:rgba(0,229,255,0.08);margin:0">', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-label">// Summary</div>', unsafe_allow_html=True)
            total_bullish = sum(1 for s in stocks if s["change"] >= 0)
            avg_conf = int(np.mean([s["confidence"] for s in stocks]))
            st.markdown(f"""
            <div class="metric-box" style="margin-bottom:10px">
                <div class="metric-label">Stocks Detected</div>
                <div class="metric-value cyan">{len(stocks)}</div>
            </div>
            <div class="metric-box" style="margin-bottom:10px">
                <div class="metric-label">Avg Confidence</div>
                <div class="metric-value cyan">{avg_conf}%</div>
            </div>
            <div class="metric-box" style="margin-bottom:10px">
                <div class="metric-label">Signal Bias</div>
                <div class="metric-value {'green' if meta['type']=='bullish' else 'red'}">
                    {"BULLISH ▲" if meta['type'] == 'bullish' else "BEARISH ▼"}
                </div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Above Daily Avg</div>
                <div class="metric-value green">{total_bullish} / {len(stocks)}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Stock selected → show chart ───────────────────────────────────────────
    else:
        sym    = st.session_state.selected_stock
        s_data = next((s for s in stocks if s["symbol"] == sym), {})

        # Back button + timeframe row
        col_back, *tf_cols = st.columns([1, 1, 1, 1, 1])
        with col_back:
            if st.button("← Back"):
                st.session_state.selected_stock = None
                st.rerun()
        for i, tf in enumerate(TIMEFRAMES):
            with tf_cols[i]:
                if st.button(tf, key=f"tf_{tf}"):
                    st.session_state.selected_tf = tf
                    st.rerun()

        # Active timeframe badge
        st.markdown(f"""
        <div style="margin:10px 0 16px;font-family:'Space Mono',monospace;
                    font-size:0.78rem;color:#64748b">
            Active Timeframe:&nbsp;
            <span style="color:#00e5ff;background:rgba(0,229,255,0.1);
                         padding:2px 10px;border-radius:4px">
                {st.session_state.selected_tf}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Metric strip
        if s_data:
            chg_cls = "green" if s_data["change"] >= 0 else "red"
            chg_sign = "+" if s_data["change"] >= 0 else ""
            conf_color = "#00e676" if s_data["confidence"] >= 90 else \
                         "#ffd600" if s_data["confidence"] >= 80 else "#ff9100"
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-box">
                    <div class="metric-label">Symbol</div>
                    <div class="metric-value cyan">{sym}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">LTP</div>
                    <div class="metric-value">₹{s_data['ltp']:,.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Change</div>
                    <div class="metric-value {chg_cls}">{chg_sign}{s_data['change']}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Pattern</div>
                    <div class="metric-value" style="font-size:0.85rem">{pattern}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Confidence</div>
                    <div class="metric-value" style="color:{conf_color}">{s_data['confidence']}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Chart
        with st.spinner("Loading chart…"):
            df  = generate_ohlcv(pattern, st.session_state.selected_tf)
            fig = build_chart(df, sym, pattern, st.session_state.selected_tf)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Pattern description box
        st.markdown(f"""
        <div style="background:#111827;border:1px solid rgba(0,229,255,0.15);
                    border-left:3px solid #00e5ff;border-radius:8px;
                    padding:16px 20px;margin-top:8px">
            <div style="font-family:'Space Mono',monospace;font-size:0.72rem;
                        color:#00e5ff;text-transform:uppercase;letter-spacing:0.1em;
                        margin-bottom:8px">Pattern Insight</div>
            <div style="font-size:0.85rem;color:#94a3b8;line-height:1.7">
                {PATTERNS[pattern]['description']}
                The pattern has been detected in the <strong style='color:#e2e8f0'>
                {st.session_state.selected_tf}</strong> timeframe for
                <strong style='color:#00e5ff'>{sym}</strong> with a confidence
                score of <strong style='color:#00e5ff'>{s_data.get('confidence','–')}%</strong>.
                Consider volume confirmation and broader market context before
                making any trading decisions.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:48px;padding-top:16px;border-top:1px solid rgba(0,229,255,0.08);
            text-align:center;font-size:0.72rem;color:#334155;font-family:'Space Mono',monospace">
    CHARTSCAN · FOR EDUCATIONAL PURPOSES ONLY · NOT FINANCIAL ADVICE
</div>
""", unsafe_allow_html=True)
