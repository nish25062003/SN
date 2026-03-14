"""
ChartScan – Stock Pattern Detector
Real candle data via AngelOne SmartAPI (smartapi-python)

Requirements:
    pip install streamlit plotly pandas numpy smartapi-python pyotp pytz
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pyotp
import pytz

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChartScan – Pattern Detection",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:#0a0e1a; --bg2:#111827; --bg3:#1a2235;
    --accent:#00e5ff; --green:#00e676; --red:#ff1744;
    --yellow:#ffd600; --text:#e2e8f0; --muted:#64748b;
    --border:rgba(0,229,255,0.15);
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3,h4{font-family:'Space Mono',monospace!important;}
input,.stTextInput input{background:var(--bg3)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:6px!important;font-family:'Space Mono',monospace!important;}
.stSelectbox>div>div{background:var(--bg2)!important;border-color:var(--border)!important;color:var(--text)!important;}
.header-banner{background:linear-gradient(135deg,#0a0e1a 0%,#111827 50%,#0d1525 100%);border:1px solid var(--border);border-radius:12px;padding:28px 36px;margin-bottom:24px;position:relative;overflow:hidden;}
.header-banner::before{content:'';position:absolute;top:-50%;right:-10%;width:400px;height:400px;background:radial-gradient(circle,rgba(0,229,255,0.06) 0%,transparent 70%);pointer-events:none;}
.header-title{font-family:'Space Mono',monospace;font-size:2rem;font-weight:700;color:var(--accent);margin:0 0 4px 0;}
.header-sub{color:var(--muted);font-size:0.9rem;margin:0;letter-spacing:0.05em;text-transform:uppercase;}
.section-label{font-family:'Space Mono',monospace;font-size:0.72rem;color:var(--accent);text-transform:uppercase;letter-spacing:0.12em;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--border);}
.pattern-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin-bottom:8px;}
.pattern-card.selected{border-color:var(--accent);background:var(--bg3);box-shadow:0 0 20px rgba(0,229,255,0.1);}
.pattern-name{font-family:'Space Mono',monospace;font-size:0.82rem;font-weight:700;color:var(--text);}
.badge-bearish{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.68rem;font-family:'Space Mono',monospace;font-weight:700;background:rgba(255,23,68,0.15);color:var(--red);}
.badge-bullish{display:inline-block;padding:2px 8px;border-radius:4px;font-size:0.68rem;font-family:'Space Mono',monospace;font-weight:700;background:rgba(0,230,118,0.15);color:var(--green);}
.metric-box{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:14px 18px;margin-bottom:10px;}
.metric-label{font-size:0.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;}
.metric-value{font-family:'Space Mono',monospace;font-size:1.05rem;font-weight:700;color:var(--text);margin-top:4px;}
.metric-value.green{color:var(--green);} .metric-value.red{color:var(--red);} .metric-value.cyan{color:var(--accent);}
.login-box{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:32px 36px;max-width:480px;margin:40px auto;}
.stock-sym{font-family:'Space Mono',monospace;font-size:0.95rem;font-weight:700;color:var(--accent);}
hr.divider{border-color:rgba(0,229,255,0.08);margin:4px 0;}
::-webkit-scrollbar{width:5px;} ::-webkit-scrollbar-track{background:var(--bg);} ::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px;}
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
PATTERNS = {
    "Double Top":               {"type": "bearish", "icon": "⛰️",  "desc": "Two consecutive peaks at similar levels — signals reversal from uptrend."},
    "Triple Top":               {"type": "bearish", "icon": "🏔️",  "desc": "Three peaks at similar levels before a downside breakout."},
    "Head & Shoulders":         {"type": "bearish", "icon": "👤",  "desc": "Left shoulder → higher head → right shoulder; classic topping pattern."},
    "Reverse Head & Shoulders": {"type": "bullish", "icon": "🔄",  "desc": "Inverse H&S; signals reversal from downtrend to uptrend."},
    "Reverse Double Top":       {"type": "bullish", "icon": "📈",  "desc": "Two troughs at similar lows — signals a shift to uptrend."},
    "Reverse Triple Top":       {"type": "bullish", "icon": "🚀",  "desc": "Three lows at similar levels before an upside breakout."},
}

# symbol → (exchange, symboltoken)  — tokens from AngelOne instrument list
WATCHLIST = {
    "RELIANCE":    ("NSE", "2885"),
    "HDFCBANK":    ("NSE", "1333"),
    "INFY":        ("NSE", "1594"),
    "TCS":         ("NSE", "11536"),
    "ICICIBANK":   ("NSE", "4963"),
    "AXISBANK":    ("NSE", "5900"),
    "SBIN":        ("NSE", "3045"),
    "WIPRO":       ("NSE", "3787"),
    "BAJFINANCE":  ("NSE", "317"),
    "TATASTEEL":   ("NSE", "3499"),
    "SUNPHARMA":   ("NSE", "3351"),
    "KOTAKBANK":   ("NSE", "1922"),
    "MARUTI":      ("NSE", "10999"),
    "TITAN":       ("NSE", "3506"),
    "ASIANPAINT":  ("NSE", "236"),
    "NESTLEIND":   ("NSE", "17963"),
    "DRREDDY":     ("NSE", "881"),
    "HINDUNILVR":  ("NSE", "1394"),
    "LT":          ("NSE", "11483"),
    "ONGC":        ("NSE", "2475"),
}

# AngelOne interval strings
TF_MAP = {
    "5 Min":  "FIVE_MINUTE",
    "15 Min": "FIFTEEN_MINUTE",
    "1 Hour": "ONE_HOUR",
    "Daily":  "ONE_DAY",
}

# How many days back to fetch for each timeframe
TF_DAYS = {
    "5 Min":  30,
    "15 Min": 60,
    "1 Hour": 150,
    "Daily":  365,
}

TIMEFRAMES = list(TF_MAP.keys())

# ─── Session State ────────────────────────────────────────────────────────────
for k, v in {
    "logged_in": False, "smart_api": None,
    "selected_pattern": None, "selected_stock": None,
    "selected_tf": "Daily", "detected_stocks": {},
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── AngelOne Helpers ─────────────────────────────────────────────────────────
def angel_login(api_key, client_id, password, totp_secret):
    """Login to AngelOne SmartAPI and return SmartConnect object."""
    try:
        from SmartApi import SmartConnect
        obj  = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(totp_secret).now()
        data = obj.generateSession(client_id, password, totp)
        if not data or not data.get("status"):
            return None, data.get("message", "Login failed")
        return obj, "OK"
    except Exception as e:
        return None, str(e)


def fetch_candles(obj, symbol, timeframe):
    """Fetch OHLCV candle data from AngelOne for a given symbol and timeframe."""
    exchange, token = WATCHLIST[symbol]
    days     = TF_DAYS[timeframe]
    interval = TF_MAP[timeframe]
    ist      = pytz.timezone("Asia/Kolkata")
    to_dt    = datetime.now(ist)
    from_dt  = to_dt - timedelta(days=days)
    params   = {
        "exchange":    exchange,
        "symboltoken": token,
        "interval":    interval,
        "fromdate":    from_dt.strftime("%Y-%m-%d %H:%M"),
        "todate":      to_dt.strftime("%Y-%m-%d %H:%M"),
    }
    try:
        resp = obj.getCandleData(params)
        raw  = resp.get("data", [])
        if not raw:
            return pd.DataFrame()
        df = pd.DataFrame(raw, columns=["time","open","high","low","close","volume"])
        df["time"] = pd.to_datetime(df["time"])
        df[["open","high","low","close","volume"]] = (
            df[["open","high","low","close","volume"]].apply(pd.to_numeric)
        )
        return df
    except Exception as e:
        st.error(f"Data fetch error for {symbol}: {e}")
        return pd.DataFrame()


# ─── Pattern Detection ────────────────────────────────────────────────────────
def find_pivots(close, order=5):
    highs, lows = [], []
    for i in range(order, len(close) - order):
        window = close[i - order: i + order + 1]
        if close[i] == window.max(): highs.append(i)
        if close[i] == window.min(): lows.append(i)
    return highs, lows


def detect_pattern(df, pattern):
    """Returns (detected: bool, confidence: float)."""
    if df.empty or len(df) < 40:
        return False, 0.0
    close  = df["close"].values
    highs, lows = find_pivots(close, order=5)
    try:
        if pattern == "Double Top" and len(highs) >= 2:
            h1, h2 = close[highs[-2]], close[highs[-1]]
            diff   = abs(h1 - h2) / max(h1, h2)
            if diff < 0.03:
                return True, round(95 - diff * 1000, 1)

        elif pattern == "Triple Top" and len(highs) >= 3:
            h1, h2, h3 = close[highs[-3]], close[highs[-2]], close[highs[-1]]
            avg    = (h1 + h2 + h3) / 3
            spread = max(h1, h2, h3) - min(h1, h2, h3)
            if spread / avg < 0.04:
                return True, round(93 - (spread / avg) * 500, 1)

        elif pattern == "Head & Shoulders" and len(highs) >= 3:
            ls, head, rs = close[highs[-3]], close[highs[-2]], close[highs[-1]]
            if head > ls and head > rs and abs(ls - rs) / head < 0.05:
                sym = 1 - abs(ls - rs) / head
                return True, round(88 * sym, 1)

        elif pattern == "Reverse Head & Shoulders" and len(lows) >= 3:
            ls, head, rs = close[lows[-3]], close[lows[-2]], close[lows[-1]]
            if head < ls and head < rs and abs(ls - rs) / ls < 0.05:
                sym = 1 - abs(ls - rs) / ls
                return True, round(88 * sym, 1)

        elif pattern == "Reverse Double Top" and len(lows) >= 2:
            l1, l2 = close[lows[-2]], close[lows[-1]]
            diff   = abs(l1 - l2) / min(l1, l2)
            if diff < 0.03:
                return True, round(95 - diff * 1000, 1)

        elif pattern == "Reverse Triple Top" and len(lows) >= 3:
            l1, l2, l3 = close[lows[-3]], close[lows[-2]], close[lows[-1]]
            avg    = (l1 + l2 + l3) / 3
            spread = max(l1, l2, l3) - min(l1, l2, l3)
            if spread / avg < 0.04:
                return True, round(93 - (spread / avg) * 500, 1)
    except Exception:
        pass
    return False, 0.0


@st.cache_data(ttl=300, show_spinner=False)
def scan_all_patterns(_obj, timeframe):
    """
    Scan all watchlist stocks for every pattern.
    Returns { pattern_name: [ {symbol, ltp, change, confidence}, ... ] }
    Result is cached for 5 minutes.
    """
    results = {p: [] for p in PATTERNS}
    prog    = st.progress(0, text="Scanning stocks…")
    total   = len(WATCHLIST)
    for idx, symbol in enumerate(WATCHLIST):
        prog.progress((idx + 1) / total, text=f"Scanning {symbol}…")
        df = fetch_candles(_obj, symbol, timeframe)
        if df.empty:
            continue
        ltp    = float(df["close"].iloc[-1])
        prev   = float(df["close"].iloc[-2]) if len(df) > 1 else ltp
        change = round((ltp - prev) / prev * 100, 2)
        for pname in PATTERNS:
            found, conf = detect_pattern(df, pname)
            if found:
                results[pname].append({
                    "symbol":     symbol,
                    "ltp":        ltp,
                    "change":     change,
                    "confidence": conf,
                })
    prog.empty()
    return results


# ─── Chart Builder ────────────────────────────────────────────────────────────
def build_chart(df, symbol, pattern, timeframe):
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

    # EMA overlays
    df = df.copy()
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    fig.add_trace(go.Scatter(x=df["time"], y=df["ema20"], name="EMA 20",
                             line=dict(color="rgba(0,229,255,0.8)", width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["ema50"], name="EMA 50",
                             line=dict(color="rgba(255,214,0,0.6)", width=1.2)), row=1, col=1)

    # Volume bars
    colors = ["rgba(0,230,118,0.5)" if c >= o else "rgba(255,23,68,0.5)"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Volume",
                         marker_color=colors, showlegend=False), row=2, col=1)

    # Highlight last 30% as pattern zone
    n = len(df)
    z = int(n * 0.70)
    fig.add_shape(type="rect",
                  x0=df["time"].iloc[z], x1=df["time"].iloc[-1],
                  y0=df["low"].iloc[z:].min() * 0.995,
                  y1=df["high"].iloc[z:].max() * 1.005,
                  fillcolor="rgba(0,229,255,0.04)",
                  line=dict(color="rgba(0,229,255,0.3)", width=1, dash="dot"),
                  row=1, col=1)
    fig.add_annotation(x=df["time"].iloc[-1],
                       y=df["high"].iloc[z:].max() * 1.005,
                       text=f"  {pattern}", showarrow=False,
                       font=dict(color="#00e5ff", size=11, family="Space Mono"),
                       xanchor="right", row=1, col=1)

    fig.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
        font=dict(color="#e2e8f0", family="DM Sans"),
        title=dict(text=f"<b>{symbol}</b>  ·  {timeframe}  ·  {pattern}",
                   font=dict(color="#00e5ff", size=15, family="Space Mono"), x=0.01),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", x=0, y=1.02,
                    font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10), height=540,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        xaxis2=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis2=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
    )
    return fig


# ─── LOGIN SCREEN ─────────────────────────────────────────────────────────────
def login_screen():
    st.markdown("""
    <div class="header-banner">
        <div class="header-title">📡 ChartScan</div>
        <div class="header-sub">Automated Pattern Detection · Powered by AngelOne SmartAPI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Space Mono',monospace;font-size:1rem;
                color:#00e5ff;margin-bottom:20px">// Connect AngelOne Account</div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        api_key     = st.text_input("API Key",          placeholder="Your SmartAPI key")
        client_id   = st.text_input("Client ID",        placeholder="Angel One client ID")
        password    = st.text_input("Password / MPIN",  type="password", placeholder="Trading password")
        totp_secret = st.text_input(
            "TOTP Secret",
            placeholder="Base32 secret from TOTP setup",
            help="Get this at smartapi.angelbroking.com/enable-totp  →  copy the alphanumeric token shown",
        )
        submitted = st.form_submit_button("🔐  Login & Scan", use_container_width=True)

    if submitted:
        if not all([api_key, client_id, password, totp_secret]):
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Authenticating with AngelOne…"):
                obj, msg = angel_login(api_key, client_id, password, totp_secret)
            if obj:
                st.session_state.smart_api = obj
                st.session_state.logged_in = True
                st.success("Login successful! Loading dashboard…")
                st.rerun()
            else:
                st.error(f"Login failed: {msg}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;margin-top:24px;font-size:0.73rem;color:#334155;
                font-family:'Space Mono',monospace">
        Credentials are used only to call the AngelOne API · Never stored anywhere
    </div>
    """, unsafe_allow_html=True)


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
def dashboard():
    obj = st.session_state.smart_api

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="section-label">// Scan Settings</div>', unsafe_allow_html=True)
        tf = st.selectbox("Timeframe", TIMEFRAMES,
                          index=TIMEFRAMES.index(st.session_state.selected_tf),
                          label_visibility="collapsed")
        if tf != st.session_state.selected_tf:
            st.session_state.selected_tf      = tf
            st.session_state.detected_stocks  = {}
            st.session_state.selected_pattern = None
            st.session_state.selected_stock   = None

        if st.button("🔍  Scan All Stocks", use_container_width=True):
            st.session_state.detected_stocks  = {}
            st.session_state.selected_pattern = None
            st.session_state.selected_stock   = None
            with st.spinner("Fetching live data from AngelOne…"):
                st.session_state.detected_stocks = scan_all_patterns(obj, tf)
            st.rerun()

        if st.session_state.detected_stocks:
            st.markdown(
                '<div class="section-label" style="margin-top:20px">// Patterns Found</div>',
                unsafe_allow_html=True,
            )
            for pname, meta in PATTERNS.items():
                count   = len(st.session_state.detected_stocks.get(pname, []))
                badge   = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
                b_txt   = "▼" if meta["type"] == "bearish" else "▲"
                sel_cls = "selected" if st.session_state.selected_pattern == pname else ""
                st.markdown(f"""
                <div class="pattern-card {sel_cls}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="pattern-name">{meta['icon']} {pname}</div>
                            <div style="font-size:0.7rem;color:var(--muted);margin-top:2px">
                                {count} stock{'s' if count != 1 else ''} detected
                            </div>
                        </div>
                        <span class="{badge}">{b_txt} {count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View", key=f"p_{pname}", use_container_width=True):
                    st.session_state.selected_pattern = pname
                    st.session_state.selected_stock   = None
                    st.rerun()

        st.markdown("---")
        if st.button("🚪  Logout", use_container_width=True):
            for k in ["logged_in","smart_api","selected_pattern","selected_stock"]:
                st.session_state[k] = False if k == "logged_in" else None
            st.session_state.detected_stocks = {}
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="header-banner">
        <div class="header-title">📡 ChartScan</div>
        <div class="header-sub">Live Pattern Detection · AngelOne SmartAPI · NSE / BSE</div>
    </div>
    """, unsafe_allow_html=True)

    # ── No scan yet ───────────────────────────────────────────────────────────
    if not st.session_state.detected_stocks:
        c1, c2, c3 = st.columns(3)
        for i, (pname, meta) in enumerate(PATTERNS.items()):
            badge   = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
            b_txt   = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
            with [c1, c2, c3][i % 3]:
                st.markdown(f"""
                <div class="pattern-card" style="min-height:130px">
                    <div style="font-size:2rem;margin-bottom:8px">{meta['icon']}</div>
                    <div class="pattern-name">{pname}</div>
                    <div style="margin:6px 0"><span class="{badge}">{b_txt}</span></div>
                    <div style="font-size:0.78rem;color:#64748b;margin-top:8px;line-height:1.6">
                        {meta['desc']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.info("👈  Click **Scan All Stocks** in the sidebar to fetch live data and detect patterns.")
        return

    # ── No pattern chosen yet ─────────────────────────────────────────────────
    if not st.session_state.selected_pattern:
        st.markdown('<div class="section-label">// Scan Results — Pick a Pattern</div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        for i, (pname, meta) in enumerate(PATTERNS.items()):
            stocks = st.session_state.detected_stocks.get(pname, [])
            badge  = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
            b_txt  = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
            with [c1, c2, c3][i % 3]:
                st.markdown(f"""
                <div class="pattern-card" style="min-height:120px">
                    <div style="display:flex;justify-content:space-between;align-items:start">
                        <div style="font-size:1.8rem">{meta['icon']}</div>
                        <span class="{badge}">{b_txt}</span>
                    </div>
                    <div class="pattern-name" style="margin-top:8px">{pname}</div>
                    <div style="font-family:'Space Mono',monospace;color:#00e5ff;
                                font-size:0.85rem;margin-top:8px">
                        {len(stocks)} stock{'s' if len(stocks)!=1 else ''} →
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Explore", key=f"exp_{pname}", use_container_width=True):
                    st.session_state.selected_pattern = pname
                    st.session_state.selected_stock   = None
                    st.rerun()
        return

    # ── Pattern selected ──────────────────────────────────────────────────────
    pattern = st.session_state.selected_pattern
    meta    = PATTERNS[pattern]
    stocks  = st.session_state.detected_stocks.get(pattern, [])

    # Breadcrumb
    bc_stock = (f"› <span style='color:#e2e8f0'>{st.session_state.selected_stock}</span>"
                if st.session_state.selected_stock else "")
    st.markdown(f"""
    <div style="font-size:0.78rem;color:#64748b;margin-bottom:18px;
                font-family:'Space Mono',monospace">
        HOME › <span style="color:#00e5ff">{pattern.upper()}</span> {bc_stock}
    </div>
    """, unsafe_allow_html=True)

    # ── Stock list ────────────────────────────────────────────────────────────
    if not st.session_state.selected_stock:
        left, right = st.columns([2.2, 1])
        with left:
            badge_cls = "badge-bearish" if meta["type"] == "bearish" else "badge-bullish"
            b_txt     = "▼ BEARISH" if meta["type"] == "bearish" else "▲ BULLISH"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:18px">
                <span style="font-size:2.2rem">{meta['icon']}</span>
                <div>
                    <div style="font-family:'Space Mono',monospace;font-size:1.2rem;
                                font-weight:700;color:#e2e8f0">{pattern}</div>
                    <span class="{badge_cls}" style="display:inline-block;margin-top:4px">
                        {b_txt}
                    </span>
                </div>
            </div>
            <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:20px;
                        line-height:1.6;max-width:520px">{meta['desc']}</div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-label">// Stocks with Pattern Detected</div>',
                        unsafe_allow_html=True)

            if not stocks:
                st.warning("No stocks matched this pattern in the current scan. Try a different timeframe.")
            else:
                for s in sorted(stocks, key=lambda x: -x["confidence"]):
                    chg_s   = "+" if s["change"] >= 0 else ""
                    chg_clr = "#00e676" if s["change"] >= 0 else "#ff1744"
                    cf_clr  = "#00e676" if s["confidence"] >= 85 else \
                              "#ffd600" if s["confidence"] >= 70 else "#ff9100"
                    ci, cp, cb = st.columns([3, 2, 1])
                    with ci:
                        st.markdown(f"""
                        <div style="padding:10px 0">
                            <div class="stock-sym">{s['symbol']}</div>
                        </div>""", unsafe_allow_html=True)
                    with cp:
                        st.markdown(f"""
                        <div style="padding:10px 0;text-align:right">
                            <div style="font-family:'Space Mono',monospace;font-size:0.9rem">
                                ₹{s['ltp']:,.2f}</div>
                            <div style="color:{chg_clr};font-family:'Space Mono',monospace;
                                        font-size:0.82rem">{chg_s}{s['change']}%</div>
                            <div style="font-size:0.68rem;color:{cf_clr};
                                        font-family:'Space Mono',monospace">
                                ⬤ {s['confidence']}% conf
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with cb:
                        if st.button("Analyze →", key=f"s_{s['symbol']}"):
                            st.session_state.selected_stock = s["symbol"]
                            st.rerun()
                    st.markdown('<hr class="divider">', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-label">// Summary</div>', unsafe_allow_html=True)
            avg_conf = round(np.mean([s["confidence"] for s in stocks]), 1) if stocks else 0
            bull_cnt = sum(1 for s in stocks if s["change"] >= 0)
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Detected</div>
                <div class="metric-value cyan">{len(stocks)}</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Avg Confidence</div>
                <div class="metric-value cyan">{avg_conf}%</div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Signal Bias</div>
                <div class="metric-value {'green' if meta['type']=='bullish' else 'red'}">
                    {"BULLISH ▲" if meta['type']=='bullish' else "BEARISH ▼"}
                </div>
            </div>
            <div class="metric-box">
                <div class="metric-label">Gaining Today</div>
                <div class="metric-value green">{bull_cnt} / {len(stocks)}</div>
            </div>
            """, unsafe_allow_html=True)
        return

    # ── Chart view ────────────────────────────────────────────────────────────
    sym    = st.session_state.selected_stock
    s_data = next((s for s in stocks if s["symbol"] == sym), {})

    # Back + timeframe row
    col_back, *tf_cols = st.columns([1, 1, 1, 1, 1])
    with col_back:
        if st.button("← Back"):
            st.session_state.selected_stock = None
            st.rerun()
    for i, tf_label in enumerate(TIMEFRAMES):
        with tf_cols[i]:
            if st.button(tf_label, key=f"tf_{tf_label}"):
                st.session_state.selected_tf = tf_label
                st.rerun()

    st.markdown(f"""
    <div style="margin:10px 0 14px;font-family:'Space Mono',monospace;
                font-size:0.78rem;color:#64748b">
        Active:&nbsp;
        <span style="color:#00e5ff;background:rgba(0,229,255,0.1);
                     padding:2px 10px;border-radius:4px">
            {st.session_state.selected_tf}
        </span>
    </div>""", unsafe_allow_html=True)

    # Metric strip
    if s_data:
        chg_c = "green" if s_data["change"] >= 0 else "red"
        chg_s = "+" if s_data["change"] >= 0 else ""
        cf_c  = "#00e676" if s_data["confidence"] >= 85 else "#ffd600"
        st.markdown(f"""
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">
            <div class="metric-box" style="flex:1;min-width:90px">
                <div class="metric-label">Symbol</div>
                <div class="metric-value cyan">{sym}</div>
            </div>
            <div class="metric-box" style="flex:1;min-width:90px">
                <div class="metric-label">LTP</div>
                <div class="metric-value">₹{s_data['ltp']:,.2f}</div>
            </div>
            <div class="metric-box" style="flex:1;min-width:90px">
                <div class="metric-label">Change</div>
                <div class="metric-value {chg_c}">{chg_s}{s_data['change']}%</div>
            </div>
            <div class="metric-box" style="flex:1;min-width:130px">
                <div class="metric-label">Pattern</div>
                <div class="metric-value" style="font-size:0.82rem">{pattern}</div>
            </div>
            <div class="metric-box" style="flex:1;min-width:90px">
                <div class="metric-label">Confidence</div>
                <div class="metric-value" style="color:{cf_c}">{s_data['confidence']}%</div>
            </div>
        </div>""", unsafe_allow_html=True)

    with st.spinner(f"Loading {sym} · {st.session_state.selected_tf} from AngelOne…"):
        df = fetch_candles(obj, sym, st.session_state.selected_tf)

    if df.empty:
        st.error("Could not fetch candle data. Token may have expired — please re-login.")
    else:
        fig = build_chart(df, sym, pattern, st.session_state.selected_tf)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div style="background:#111827;border:1px solid rgba(0,229,255,0.15);
                border-left:3px solid #00e5ff;border-radius:8px;
                padding:16px 20px;margin-top:8px">
        <div style="font-family:'Space Mono',monospace;font-size:0.72rem;
                    color:#00e5ff;text-transform:uppercase;letter-spacing:0.1em;
                    margin-bottom:8px">Pattern Insight</div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.7">
            {meta['desc']}&nbsp;Detected on
            <strong style="color:#e2e8f0">{st.session_state.selected_tf}</strong>
            chart of <strong style="color:#00e5ff">{sym}</strong> with confidence
            <strong style="color:#00e5ff">{s_data.get('confidence','–')}%</strong>.
            Confirm with volume and broader market context before trading.
        </div>
    </div>""", unsafe_allow_html=True)


# ─── Entry Point ──────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    login_screen()
else:
    dashboard()

st.markdown("""
<div style="margin-top:48px;padding-top:16px;border-top:1px solid rgba(0,229,255,0.08);
            text-align:center;font-size:0.72rem;color:#334155;font-family:'Space Mono',monospace">
    CHARTSCAN · FOR EDUCATIONAL USE ONLY · NOT FINANCIAL ADVICE
</div>
""", unsafe_allow_html=True)
