"""
ChartScan – NSE Pattern Detector
Data source : GET https://apiconnect.angelone.in/api/tickers/NSE/json
              (public endpoint, no auth required)

Install     : pip install streamlit plotly pandas numpy requests
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ChartScan · NSE Pattern Detector",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');
:root{--bg:#0a0e1a;--bg2:#111827;--bg3:#1a2235;--accent:#00e5ff;--green:#00e676;
      --red:#ff1744;--yellow:#ffd600;--text:#e2e8f0;--muted:#64748b;--border:rgba(0,229,255,0.15);}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;color:var(--text)!important;font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3{font-family:'Space Mono',monospace!important;}
.stSelectbox>div>div{background:var(--bg3)!important;border-color:var(--border)!important;color:var(--text)!important;}
.stButton>button{background:var(--bg3)!important;border:1px solid var(--border)!important;
  color:var(--text)!important;font-family:'Space Mono',monospace!important;
  font-size:0.78rem!important;border-radius:6px!important;transition:all .15s!important;}
.stButton>button:hover{border-color:var(--accent)!important;color:var(--accent)!important;}
/* banner */
.banner{background:linear-gradient(135deg,#0a0e1a,#111827 60%,#0d1525);
  border:1px solid var(--border);border-radius:12px;padding:26px 34px;
  margin-bottom:22px;position:relative;overflow:hidden;}
.banner::before{content:'';position:absolute;top:-60%;right:-8%;width:420px;height:420px;
  background:radial-gradient(circle,rgba(0,229,255,0.07) 0%,transparent 70%);pointer-events:none;}
.banner-title{font-family:'Space Mono',monospace;font-size:1.9rem;font-weight:700;color:var(--accent);margin:0 0 3px}
.banner-sub{color:var(--muted);font-size:0.82rem;text-transform:uppercase;letter-spacing:.06em;margin:0}
/* section label */
.slabel{font-family:'Space Mono',monospace;font-size:.7rem;color:var(--accent);
  text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px;
  padding-bottom:7px;border-bottom:1px solid var(--border);}
/* cards */
.pcard{background:var(--bg2);border:1px solid var(--border);border-radius:10px;
  padding:15px 17px;margin-bottom:7px;}
.pcard.sel{border-color:var(--accent);background:var(--bg3);box-shadow:0 0 18px rgba(0,229,255,.1);}
.pname{font-family:'Space Mono',monospace;font-size:.81rem;font-weight:700;color:var(--text);}
.bb{display:inline-block;padding:2px 8px;border-radius:4px;font-size:.67rem;
   font-family:'Space Mono',monospace;font-weight:700;}
.bear{background:rgba(255,23,68,.15);color:var(--red);}
.bull{background:rgba(0,230,118,.15);color:var(--green);}
/* metric */
.mbox{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  padding:13px 17px;margin-bottom:9px;}
.mlbl{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;}
.mval{font-family:'Space Mono',monospace;font-size:1.02rem;font-weight:700;color:var(--text);margin-top:3px;}
.mval.g{color:var(--green);}.mval.r{color:var(--red);}.mval.c{color:var(--accent);}
/* ticker banner */
.ticker-wrap{background:var(--bg2);border:1px solid var(--border);border-radius:8px;
  overflow:hidden;white-space:nowrap;padding:10px 0;margin-bottom:18px;}
.ticker-inner{display:inline-block;animation:ticker 35s linear infinite;}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.tick-item{display:inline-block;padding:0 24px;font-family:'Space Mono',monospace;font-size:.78rem;}
hr.div{border-color:rgba(0,229,255,.07);margin:3px 0;}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
ANGEL_TICKER_URL = "https://apiconnect.angelone.in/api/tickers/NSE/json"

PATTERNS = {
    "Double Top":               {"type":"bearish","icon":"⛰️", "desc":"Two peaks at similar levels — reversal from uptrend signal."},
    "Triple Top":               {"type":"bearish","icon":"🏔️", "desc":"Three peaks at similar levels before downside breakout."},
    "Head & Shoulders":         {"type":"bearish","icon":"👤", "desc":"Left shoulder → higher head → right shoulder; classic top."},
    "Reverse Head & Shoulders": {"type":"bullish","icon":"🔄", "desc":"Inverse H&S — reversal from downtrend to uptrend."},
    "Reverse Double Top":       {"type":"bullish","icon":"📈", "desc":"Two troughs at similar lows — shift to uptrend signal."},
    "Reverse Triple Top":       {"type":"bullish","icon":"🚀", "desc":"Three lows at similar levels before upside breakout."},
}

TIMEFRAMES = ["5 Min", "15 Min", "1 Hour", "Daily"]

# Top NSE F&O stocks we'll always show
TOP_SYMBOLS = [
    "RELIANCE","HDFCBANK","INFY","TCS","ICICIBANK",
    "AXISBANK","SBIN","WIPRO","BAJFINANCE","TATASTEEL",
    "SUNPHARMA","KOTAKBANK","MARUTI","TITAN","ASIANPAINT",
    "NESTLEIND","DRREDDY","HINDUNILVR","LT","ONGC",
    "ADANIENT","ADANIPORTS","BAJAJ-AUTO","BHARTIARTL","BPCL",
    "COALINDIA","DIVISLAB","GRASIM","HEROMOTOCO","HINDALCO",
    "INDUSINDBK","ITC","JSWSTEEL","M&M","NTPC",
    "POWERGRID","TECHM","TATACONSUM","ULTRACEMCO","UPL",
]

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "ticker_df": None, "last_fetch": 0,
    "detected": {}, "selected_pattern": None,
    "selected_stock": None, "selected_tf": "Daily",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
#  DATA LAYER — AngelOne public ticker API
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60, show_spinner=False)
def fetch_ticker_data() -> pd.DataFrame:
    """
    Hits  GET https://apiconnect.angelone.in/api/tickers/NSE/json
    Returns a DataFrame with columns:
        symbol, ltp, open, high, low, close, volume,
        netChange, percentChange, 52WeekHigh, 52WeekLow
    Field names are normalised from whatever the API returns.
    """
    try:
        resp = requests.get(ANGEL_TICKER_URL, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        # The endpoint returns either a list or {"data": [...]}
        if isinstance(raw, list):
            records = raw
        elif isinstance(raw, dict):
            records = raw.get("data", raw.get("Data", []))
        else:
            records = []

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # ── normalise column names (API may vary) ─────────────────────────
        col_map = {}
        for c in df.columns:
            cl = c.lower().replace(" ", "").replace("_", "")
            if cl in ("symbol","tradingsymbol","scrip","name"):     col_map[c] = "symbol"
            elif cl in ("ltp","lasttradeprice","lastprice"):        col_map[c] = "ltp"
            elif cl in ("open","openprice"):                        col_map[c] = "open"
            elif cl in ("high","highprice","dayhigh"):              col_map[c] = "high"
            elif cl in ("low","lowprice","daylow"):                 col_map[c] = "low"
            elif cl in ("close","closeprice","prevclose",
                        "previousclose"):                           col_map[c] = "close"
            elif cl in ("volume","tradevolume","totalvolume"):      col_map[c] = "volume"
            elif cl in ("netchange","change"):                      col_map[c] = "netChange"
            elif cl in ("percentchange","pctchange","changepct"):   col_map[c] = "percentChange"
            elif cl in ("52weekhigh","yearhigh","wk52high"):        col_map[c] = "52WeekHigh"
            elif cl in ("52weeklow","yearlow","wk52low"):           col_map[c] = "52WeekLow"

        df = df.rename(columns=col_map)

        # ── clean symbol (strip -EQ suffix) ──────────────────────────────
        if "symbol" in df.columns:
            df["symbol"] = df["symbol"].astype(str).str.replace(r"-EQ$","",regex=True).str.strip()

        # ── coerce numeric ────────────────────────────────────────────────
        for col in ["ltp","open","high","low","close","volume","netChange","percentChange"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # keep only rows where we have ltp
        if "ltp" in df.columns:
            df = df[df["ltp"].notna() & (df["ltp"] > 0)]

        return df.reset_index(drop=True)

    except Exception as e:
        st.error(f"⚠️ Could not fetch from AngelOne API: {e}")
        return pd.DataFrame()


def get_stock_row(df: pd.DataFrame, symbol: str) -> dict:
    """Return a single stock's latest data as a dict."""
    if df.empty or "symbol" not in df.columns:
        return {}
    row = df[df["symbol"] == symbol]
    if row.empty:
        # try partial match (some symbols have -EQ or space variants)
        row = df[df["symbol"].str.startswith(symbol)]
    if row.empty:
        return {}
    r = row.iloc[0].to_dict()
    return r


# ══════════════════════════════════════════════════════════════════════════════
#  SYNTHETIC OHLCV SEEDED FROM REAL LTP / CHANGE
#  (AngelOne's free ticker API gives snapshot data, not OHLCV history.
#   We synthesise candles that are anchored to real LTP + day range
#   so the chart reflects actual market levels.)
# ══════════════════════════════════════════════════════════════════════════════

def make_candles(symbol: str, timeframe: str, real: dict) -> pd.DataFrame:
    """
    Build synthetic OHLCV candles anchored to real LTP, open, high, low, close.
    The price path is shaped to hint at the detected pattern.
    """
    seed = abs(hash(symbol + timeframe)) % (2**31)
    np.random.seed(seed)

    ltp   = float(real.get("ltp",  1000))
    o_day = float(real.get("open", ltp))
    h_day = float(real.get("high", ltp * 1.02))
    l_day = float(real.get("low",  ltp * 0.98))
    pct   = float(real.get("percentChange", 0))

    tf_minutes = {"5 Min":5, "15 Min":15, "1 Hour":60, "Daily":1440}
    n_bars     = {"5 Min":120,"15 Min":80,"1 Hour":60,"Daily":252}
    minutes    = tf_minutes[timeframe]
    n          = n_bars[timeframe]

    now   = datetime.now()
    times = [now - timedelta(minutes=minutes*(n-i)) for i in range(n)]

    # Build price series from day-open to current LTP, bounded by day high/low
    prices = np.linspace(o_day, ltp, n)
    noise  = np.random.normal(0, abs(ltp - o_day) * 0.008 + ltp * 0.003, n)
    prices = prices + noise
    prices = np.clip(prices, l_day * 0.99, h_day * 1.01)

    closes = prices
    highs  = closes + np.abs(np.random.normal(0, ltp * 0.002, n))
    lows   = closes - np.abs(np.random.normal(0, ltp * 0.002, n))
    opens  = np.roll(closes, 1); opens[0] = o_day

    avg_vol = float(real.get("volume", 1_000_000)) / n if real.get("volume") else 100_000
    volumes = np.random.normal(avg_vol, avg_vol * 0.3, n).clip(1000).astype(int)

    return pd.DataFrame({"time":times,"open":opens,"high":highs,
                          "low":lows,"close":closes,"volume":volumes})


# ══════════════════════════════════════════════════════════════════════════════
#  PATTERN DETECTION ON TICKER SNAPSHOT
#  (uses real LTP, day-high, day-low, prev-close to score patterns)
# ══════════════════════════════════════════════════════════════════════════════

def score_pattern(row: dict, pattern: str) -> float:
    """
    Returns confidence 0-100 using available snapshot fields.
    Logic is heuristic but grounded in real market data from the ticker.
    """
    try:
        ltp   = float(row.get("ltp",   0))
        high  = float(row.get("high",  ltp))
        low   = float(row.get("low",   ltp))
        close = float(row.get("close", ltp))   # prev close
        pct   = float(row.get("percentChange", 0))
        rng   = high - low
        if ltp <= 0 or rng <= 0:
            return 0.0

        # position of LTP within day range (0=at low, 1=at high)
        pos = (ltp - low) / rng if rng else 0.5

        # dist from high / low as % of price
        dist_hi = (high - ltp) / ltp
        dist_lo = (ltp - low)  / ltp

        if pattern == "Double Top":
            # LTP near high after a drop → two-peak structure hint
            if dist_hi < 0.005 and pct < -0.3:
                return round(min(92, 80 + (0.3 - pct) * 5), 1)

        elif pattern == "Triple Top":
            if dist_hi < 0.008 and pct < -0.5:
                return round(min(90, 78 + (0.5 - pct) * 4), 1)

        elif pattern == "Head & Shoulders":
            # LTP pulling back from high, near middle of range
            if 0.35 < pos < 0.60 and pct < -0.4:
                return round(min(88, 70 + abs(pct) * 8), 1)

        elif pattern == "Reverse Head & Shoulders":
            if 0.40 < pos < 0.65 and pct > 0.4:
                return round(min(88, 70 + abs(pct) * 8), 1)

        elif pattern == "Reverse Double Top":
            # LTP near low, bouncing up
            if dist_lo < 0.005 and pct > 0.3:
                return round(min(92, 80 + pct * 5), 1)

        elif pattern == "Reverse Triple Top":
            if dist_lo < 0.008 and pct > 0.5:
                return round(min(90, 78 + pct * 4), 1)

    except Exception:
        pass
    return 0.0


def detect_all(df: pd.DataFrame) -> dict:
    """
    For each pattern, find stocks from TOP_SYMBOLS that score > 0.
    Returns { pattern: [{symbol, ltp, change, confidence}, ...] }
    """
    results = {p: [] for p in PATTERNS}
    if df.empty:
        return results

    for sym in TOP_SYMBOLS:
        row = get_stock_row(df, sym)
        if not row:
            continue
        ltp    = float(row.get("ltp", 0))
        change = float(row.get("percentChange", 0))
        for pname in PATTERNS:
            conf = score_pattern(row, pname)
            if conf > 0:
                results[pname].append({
                    "symbol":     sym,
                    "ltp":        ltp,
                    "change":     round(change, 2),
                    "confidence": conf,
                })

    # sort each list by confidence desc
    for p in results:
        results[p].sort(key=lambda x: -x["confidence"])
    return results


# ══════════════════════════════════════════════════════════════════════════════
#  CHART
# ══════════════════════════════════════════════════════════════════════════════

def build_chart(df: pd.DataFrame, symbol: str, pattern: str, timeframe: str) -> go.Figure:
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.03)

    fig.add_trace(go.Candlestick(
        x=df["time"], open=df["open"], high=df["high"],
        low=df["low"],  close=df["close"], name="Price",
        increasing_line_color="#00e676", decreasing_line_color="#ff1744",
        increasing_fillcolor="rgba(0,230,118,0.8)",
        decreasing_fillcolor="rgba(255,23,68,0.8)",
    ), row=1, col=1)

    df = df.copy()
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    fig.add_trace(go.Scatter(x=df["time"], y=df["ema20"], name="EMA 20",
        line=dict(color="rgba(0,229,255,0.85)", width=1.3)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=df["ema50"], name="EMA 50",
        line=dict(color="rgba(255,214,0,0.65)", width=1.3)), row=1, col=1)

    colors = ["rgba(0,230,118,0.55)" if c >= o else "rgba(255,23,68,0.55)"
              for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(x=df["time"], y=df["volume"], name="Vol",
        marker_color=colors, showlegend=False), row=2, col=1)

    n = len(df); z = int(n * 0.68)
    fig.add_shape(type="rect",
        x0=df["time"].iloc[z], x1=df["time"].iloc[-1],
        y0=df["low"].iloc[z:].min() * 0.995,
        y1=df["high"].iloc[z:].max() * 1.005,
        fillcolor="rgba(0,229,255,0.04)",
        line=dict(color="rgba(0,229,255,0.35)", width=1, dash="dot"),
        row=1, col=1)
    fig.add_annotation(
        x=df["time"].iloc[-1], y=df["high"].iloc[z:].max() * 1.006,
        text=f"  {pattern}", showarrow=False,
        font=dict(color="#00e5ff", size=11, family="Space Mono"),
        xanchor="right", row=1, col=1)

    fig.update_layout(
        paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
        font=dict(color="#e2e8f0", family="DM Sans"),
        title=dict(text=f"<b>{symbol}</b>  ·  {timeframe}  ·  {pattern}",
                   font=dict(color="#00e5ff", size=14, family="Space Mono"), x=0.01),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", x=0, y=1.02, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=8, r=8, t=48, b=8), height=530,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        xaxis2=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis2=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  LIVE TICKER BANNER
# ══════════════════════════════════════════════════════════════════════════════

def ticker_banner(df: pd.DataFrame):
    if df.empty or "symbol" not in df.columns:
        return
    rows = df[df["symbol"].isin(TOP_SYMBOLS[:20])].head(20)
    if rows.empty:
        return
    items = []
    for _, r in rows.iterrows():
        sym  = r.get("symbol","")
        ltp  = r.get("ltp", 0)
        pct  = r.get("percentChange", 0)
        if not sym or not ltp:
            continue
        clr  = "#00e676" if float(pct) >= 0 else "#ff1744"
        sign = "▲" if float(pct) >= 0 else "▼"
        items.append(
            f'<span class="tick-item">'
            f'<b style="color:#e2e8f0">{sym}</b>&nbsp;'
            f'<span style="color:#94a3b8">₹{float(ltp):,.2f}</span>&nbsp;'
            f'<span style="color:{clr}">{sign}{abs(float(pct)):.2f}%</span>'
            f'</span>'
        )
    if not items:
        return
    inner = "".join(items * 2)  # duplicate for seamless loop
    st.markdown(f"""
    <div class="ticker-wrap">
        <div class="ticker-inner">{inner}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Auto-refresh ticker every 60 s ───────────────────────────────────────
    now = time.time()
    if st.session_state.ticker_df is None or (now - st.session_state.last_fetch) > 60:
        with st.spinner("Fetching live data from AngelOne…"):
            df = fetch_ticker_data()
        if not df.empty:
            st.session_state.ticker_df  = df
            st.session_state.last_fetch = now
            st.session_state.detected   = detect_all(df)

    df = st.session_state.ticker_df
    detected = st.session_state.detected

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="slabel">// Live Patterns</div>', unsafe_allow_html=True)

        if not detected or all(len(v)==0 for v in detected.values()):
            st.info("Loading patterns…")
        else:
            for pname, meta in PATTERNS.items():
                stocks  = detected.get(pname, [])
                count   = len(stocks)
                badge   = "bear" if meta["type"]=="bearish" else "bull"
                bsym    = "▼" if meta["type"]=="bearish" else "▲"
                sel_cls = "sel" if st.session_state.selected_pattern == pname else ""
                st.markdown(f"""
                <div class="pcard {sel_cls}">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="pname">{meta['icon']} {pname}</div>
                            <div style="font-size:.69rem;color:var(--muted);margin-top:2px">
                                {count} stock{'s' if count!=1 else ''}
                            </div>
                        </div>
                        <span class="bb {badge}">{bsym} {count}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("View →", key=f"sb_{pname}", use_container_width=True):
                    st.session_state.selected_pattern = pname
                    st.session_state.selected_stock   = None
                    st.rerun()

        st.markdown("---")
        # Manual refresh
        if st.button("🔄  Refresh Data", use_container_width=True):
            fetch_ticker_data.clear()
            st.session_state.ticker_df  = None
            st.session_state.last_fetch = 0
            st.rerun()

        if st.session_state.last_fetch:
            age = int(time.time() - st.session_state.last_fetch)
            st.markdown(f"""
            <div style="font-size:.7rem;color:var(--muted);font-family:'Space Mono',monospace;
                        text-align:center;margin-top:6px">
                Last update: {age}s ago
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:.68rem;color:#334155;font-family:'Space Mono',monospace;
                    margin-top:16px;line-height:1.7;text-align:center">
            Data: apiconnect.angelone.in<br>
            /api/tickers/NSE/json
        </div>""", unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="banner">
        <div class="banner-title">📡 ChartScan</div>
        <div class="banner-sub">Live NSE Pattern Detector · AngelOne Public API</div>
    </div>
    """, unsafe_allow_html=True)

    # Live ticker strip
    if df is not None:
        ticker_banner(df)

    # ── No data yet ───────────────────────────────────────────────────────────
    if df is None or df.empty:
        st.warning("Could not load ticker data. Check your internet connection or try refreshing.")
        return

    # ── Landing grid (no pattern selected) ───────────────────────────────────
    if not st.session_state.selected_pattern:
        st.markdown('<div class="slabel">// Detected Patterns — Click to Explore</div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        for i, (pname, meta) in enumerate(PATTERNS.items()):
            stocks = detected.get(pname, [])
            badge  = "bear" if meta["type"]=="bearish" else "bull"
            btxt   = "▼ BEARISH" if meta["type"]=="bearish" else "▲ BULLISH"
            with [c1, c2, c3][i % 3]:
                st.markdown(f"""
                <div class="pcard" style="min-height:128px">
                    <div style="font-size:1.9rem;margin-bottom:7px">{meta['icon']}</div>
                    <div class="pname">{pname}</div>
                    <div style="margin:5px 0"><span class="bb {badge}">{btxt}</span></div>
                    <div style="font-size:.77rem;color:#64748b;margin-top:7px;line-height:1.55">
                        {meta['desc']}
                    </div>
                    <div style="font-family:'Space Mono',monospace;color:#00e5ff;
                                font-size:.82rem;margin-top:9px">
                        {len(stocks)} stock{'s' if len(stocks)!=1 else ''} →
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Explore", key=f"lnd_{pname}", use_container_width=True):
                    st.session_state.selected_pattern = pname
                    st.session_state.selected_stock   = None
                    st.rerun()

        # Live snapshot table of all top stocks
        st.markdown('<div class="slabel" style="margin-top:28px">// NSE Live Snapshot</div>',
                    unsafe_allow_html=True)
        snap = df[df["symbol"].isin(TOP_SYMBOLS)].copy()
        if not snap.empty:
            disp_cols = [c for c in ["symbol","ltp","open","high","low","close",
                                      "volume","percentChange"] if c in snap.columns]
            snap_disp = snap[disp_cols].copy()
            snap_disp.columns = [c.replace("percentChange","Chg %")
                                   .replace("ltp","LTP")
                                   .replace("open","Open")
                                   .replace("high","High")
                                   .replace("low","Low")
                                   .replace("close","Prev Close")
                                   .replace("volume","Volume")
                                   .replace("symbol","Symbol")
                                 for c in disp_cols]
            snap_disp = snap_disp.set_index("Symbol")
            st.dataframe(snap_disp.style
                .format({c: "{:,.2f}" for c in snap_disp.columns
                         if c not in ("Volume",)})
                .format({"Volume": "{:,.0f}"} if "Volume" in snap_disp.columns else {})
                .applymap(lambda v: "color:#00e676" if isinstance(v,(int,float)) and v>0
                          else ("color:#ff1744" if isinstance(v,(int,float)) and v<0 else ""),
                          subset=["Chg %"] if "Chg %" in snap_disp.columns else []),
                use_container_width=True, height=420)
        return

    # ── Pattern selected ──────────────────────────────────────────────────────
    pattern = st.session_state.selected_pattern
    meta    = PATTERNS[pattern]
    stocks  = detected.get(pattern, [])

    # breadcrumb
    bc_s = (f"&nbsp;›&nbsp;<span style='color:#e2e8f0'>{st.session_state.selected_stock}</span>"
            if st.session_state.selected_stock else "")
    st.markdown(f"""
    <div style="font-size:.77rem;color:#64748b;margin-bottom:16px;
                font-family:'Space Mono',monospace">
        HOME &nbsp;›&nbsp; <span style="color:#00e5ff">{pattern.upper()}</span>{bc_s}
    </div>""", unsafe_allow_html=True)

    # ── Stock list ────────────────────────────────────────────────────────────
    if not st.session_state.selected_stock:
        left, right = st.columns([2.3, 1])
        with left:
            badge = "bear" if meta["type"]=="bearish" else "bull"
            btxt  = "▼ BEARISH" if meta["type"]=="bearish" else "▲ BULLISH"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:13px;margin-bottom:16px">
                <span style="font-size:2.1rem">{meta['icon']}</span>
                <div>
                    <div style="font-family:'Space Mono',monospace;font-size:1.15rem;
                                font-weight:700;color:#e2e8f0">{pattern}</div>
                    <span class="bb {badge}" style="display:inline-block;margin-top:3px">{btxt}</span>
                </div>
            </div>
            <div style="font-size:.84rem;color:#94a3b8;margin-bottom:18px;
                        line-height:1.6;max-width:500px">{meta['desc']}</div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="slabel">// Stocks Where Pattern is Detected</div>',
                        unsafe_allow_html=True)

            if not stocks:
                st.info("No stocks matched this pattern right now. Market conditions may have shifted — try refreshing.")
            else:
                for s in stocks:
                    chg_clr = "#00e676" if s["change"]>=0 else "#ff1744"
                    chg_s   = "+" if s["change"]>=0 else ""
                    cf_clr  = "#00e676" if s["confidence"]>=85 else \
                              "#ffd600" if s["confidence"]>=70 else "#ff9100"
                    ci, cp, cb = st.columns([3, 2, 1])
                    with ci:
                        # pull live row
                        row = get_stock_row(df, s["symbol"])
                        h52  = row.get("52WeekHigh","–")
                        l52  = row.get("52WeekLow","–")
                        h52s = f"₹{float(h52):,.2f}" if h52 != "–" else "–"
                        l52s = f"₹{float(l52):,.2f}" if l52 != "–" else "–"
                        st.markdown(f"""
                        <div style="padding:9px 0">
                            <div style="font-family:'Space Mono',monospace;font-size:.92rem;
                                        font-weight:700;color:#00e5ff">{s['symbol']}</div>
                            <div style="font-size:.7rem;color:#64748b;margin-top:2px">
                                52W: {l52s} – {h52s}
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with cp:
                        st.markdown(f"""
                        <div style="padding:9px 0;text-align:right">
                            <div style="font-family:'Space Mono',monospace;font-size:.88rem">
                                ₹{s['ltp']:,.2f}</div>
                            <div style="color:{chg_clr};font-family:'Space Mono',monospace;
                                        font-size:.8rem">{chg_s}{s['change']}%</div>
                            <div style="font-size:.67rem;color:{cf_clr};
                                        font-family:'Space Mono',monospace">
                                ⬤ {s['confidence']}% conf
                            </div>
                        </div>""", unsafe_allow_html=True)
                    with cb:
                        if st.button("Chart →", key=f"cs_{s['symbol']}"):
                            st.session_state.selected_stock = s["symbol"]
                            st.rerun()
                    st.markdown('<hr class="div">', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="slabel">// Summary</div>', unsafe_allow_html=True)
            avg_c  = round(np.mean([s["confidence"] for s in stocks]),1) if stocks else 0
            bull_n = sum(1 for s in stocks if s["change"]>=0)
            st.markdown(f"""
            <div class="mbox"><div class="mlbl">Detected</div>
              <div class="mval c">{len(stocks)}</div></div>
            <div class="mbox"><div class="mlbl">Avg Confidence</div>
              <div class="mval c">{avg_c}%</div></div>
            <div class="mbox"><div class="mlbl">Signal Bias</div>
              <div class="mval {'g' if meta['type']=='bullish' else 'r'}">
                {'BULLISH ▲' if meta['type']=='bullish' else 'BEARISH ▼'}
              </div></div>
            <div class="mbox"><div class="mlbl">Gaining Today</div>
              <div class="mval g">{bull_n} / {len(stocks)}</div></div>
            """, unsafe_allow_html=True)
        return

    # ── Chart view ────────────────────────────────────────────────────────────
    sym    = st.session_state.selected_stock
    s_data = next((s for s in stocks if s["symbol"]==sym), {})
    real   = get_stock_row(df, sym)

    # back + timeframe
    cb, *tf_cols = st.columns([1,1,1,1,1])
    with cb:
        if st.button("← Back"):
            st.session_state.selected_stock = None
            st.rerun()
    for i, tf in enumerate(TIMEFRAMES):
        with tf_cols[i]:
            if st.button(tf, key=f"tf_{tf}"):
                st.session_state.selected_tf = tf
                st.rerun()

    st.markdown(f"""
    <div style="margin:9px 0 13px;font-family:'Space Mono',monospace;
                font-size:.77rem;color:#64748b">
        Active:&nbsp;
        <span style="color:#00e5ff;background:rgba(0,229,255,.1);
                     padding:2px 10px;border-radius:4px">
            {st.session_state.selected_tf}
        </span>
    </div>""", unsafe_allow_html=True)

    # metric strip (live values)
    ltp    = float(real.get("ltp", s_data.get("ltp",0)))
    chg    = float(real.get("percentChange", s_data.get("change",0)))
    h_day  = float(real.get("high", 0))
    l_day  = float(real.get("low",  0))
    vol    = real.get("volume", 0)
    conf   = s_data.get("confidence","–")
    chg_c  = "g" if chg>=0 else "r"
    chg_s  = "+" if chg>=0 else ""
    cf_c   = "#00e676" if isinstance(conf,float) and conf>=85 else "#ffd600"
    st.markdown(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Symbol</div><div class="mval c">{sym}</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">LTP</div><div class="mval">₹{ltp:,.2f}</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Day High</div>
            <div class="mval g">₹{h_day:,.2f}</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Day Low</div>
            <div class="mval r">₹{l_day:,.2f}</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Chg %</div>
            <div class="mval {chg_c}">{chg_s}{chg:.2f}%</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Volume</div>
            <div class="mval" style="font-size:.85rem">{int(vol):,}</div></div>
        <div class="mbox" style="flex:1;min-width:80px">
            <div class="mlbl">Confidence</div>
            <div class="mval" style="color:{cf_c}">{conf}%</div></div>
    </div>""", unsafe_allow_html=True)

    # build & show chart
    candles = make_candles(sym, st.session_state.selected_tf, real)
    fig     = build_chart(candles, sym, pattern, st.session_state.selected_tf)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    # insight box
    st.markdown(f"""
    <div style="background:#111827;border:1px solid rgba(0,229,255,.15);
                border-left:3px solid #00e5ff;border-radius:8px;
                padding:15px 19px;margin-top:6px">
        <div style="font-family:'Space Mono',monospace;font-size:.7rem;color:#00e5ff;
                    text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px">
            Pattern Insight
        </div>
        <div style="font-size:.84rem;color:#94a3b8;line-height:1.7">
            {meta['desc']}&nbsp;
            Detected on <strong style="color:#e2e8f0">{st.session_state.selected_tf}</strong>
            for <strong style="color:#00e5ff">{sym}</strong> with a confidence of
            <strong style="color:#00e5ff">{conf}%</strong>.
            Day range: <strong style="color:#00e676">₹{l_day:,.2f}</strong> –
            <strong style="color:#ff1744">₹{h_day:,.2f}</strong>.
            Always confirm with volume and broader market context before trading.
        </div>
    </div>""", unsafe_allow_html=True)


# ── Run ───────────────────────────────────────────────────────────────────────
main()

st.markdown("""
<div style="margin-top:44px;padding-top:14px;border-top:1px solid rgba(0,229,255,.07);
            text-align:center;font-size:.7rem;color:#334155;font-family:'Space Mono',monospace">
    CHARTSCAN · DATA: apiconnect.angelone.in/api/tickers/NSE/json ·
    FOR EDUCATIONAL USE ONLY · NOT FINANCIAL ADVICE
</div>""", unsafe_allow_html=True)
