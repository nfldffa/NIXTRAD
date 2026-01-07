import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import random

# ==========================================
# 1. NIXTRAD V36.0 | REGION-ADAPTIVE TERMINAL
# ==========================================
st.set_page_config(
    page_title="NIXTRAD | ADAPTIVE ENGINE",
    layout="wide",
    page_icon="💹",
    initial_sidebar_state="expanded"
)

# Kunci Seed (Deterministic)
np.random.seed(42)
random.seed(42)

# Custom CSS Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    :root { --bg: #000; --card: #0a0a0a; --bull: #00ff88; --bear: #ff3355; --accent: #0088ff; }
    .stApp { background-color: var(--bg); color: #fff; font-family: 'Inter', sans-serif; }
    
    /* SIDEBAR LOCK & BRANDING */
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a !important; }
    .sidebar-brand { font-size: 2.2rem; font-weight: 800; letter-spacing: -2px; color: #fff; text-align: center; margin-bottom: 25px; padding-top: 10px; }
    .sidebar-brand span { color: var(--bull); }

    /* BENTO BOX DESIGN */
    .bento-card { background: var(--card); border: 1px solid #1a1a1a; border-radius: 12px; padding: 22px; height: 100%; transition: 0.3s; }
    .bento-card:hover { border-color: #333; box-shadow: 0 10px 30px rgba(0,0,0,0.7); }
    .metric-title { color: #666; font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 8px;}
    .metric-value { font-family: 'JetBrains Mono'; font-size: 1.9rem; font-weight: 800; line-height: 1.1; }
    
    /* STATUS BADGE */
    .status-badge { padding: 6px 14px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; display: inline-block; margin-top: 5px; }
    .open { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .closed { background: rgba(255, 51, 85, 0.1); color: #ff3355; border: 1px solid #ff3355; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE UTILITIES
# ==========================================
def format_currency(value, ticker):
    symbol = "Rp" if ".JK" in ticker else "$"
    if symbol == "Rp":
        return f"{symbol} {value:,.0f}"
    else:
        return f"{symbol}{value:,.2f}"

def get_market_status(ticker):
    try:
        if ".JK" in ticker:
            jkt = datetime.now(pytz.timezone('Asia/Jakarta'))
            if jkt.weekday() < 5 and 9 <= jkt.hour < 16: return "OPEN (IDX)", "open"
            return "CLOSED (IDX)", "closed"
        else:
            est = datetime.now(pytz.timezone('US/Eastern'))
            if est.weekday() < 5 and 9 <= est.hour < 16: return "OPEN (NYSE)", "open"
            return "CLOSED (NYSE)", "closed"
    except:
        return "N/A", "closed"

@st.cache_data(ttl=60)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="5y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return None, None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df['SMA_200'] = df['Close'].rolling(200).mean()
        last_upd = df['Date'].iloc[-1].strftime("%d %b %Y | %H:%M")
        return df.dropna(), last_upd
    except: 
        return None, None

# ==========================================
# 3. REGION-ADAPTIVE ENGINE (FINAL OPTIMIZATION)
# ==========================================
def GOLDEN_Engine(df, ticker, days):
    # Scalar Values
    last_p = float(df['Close'].iloc[-1])
    sma_200 = float(df['SMA_200'].iloc[-1])
    is_idx = ".JK" in ticker
    
    # 1. MULTI-TIMEFRAME ANALYSIS
    mu_long = df['Close'].pct_change().mean()     # 5 Tahun
    mu_mid = df.tail(252)['Close'].pct_change().mean() # 1 Tahun
    mu_short = df.tail(21)['Close'].pct_change().mean() # 1 Bulan (Micro-trend)
    
    # 2. REGION-BASED DRIFT WEIGHTING
    if is_idx:
        # Untuk Saham Indonesia: Lebih stabil, bobot merata agar tidak gampang minus
        # Menghargai micro-trend (mu_short) jika sedang rebound
        weight_short = 0.30 if mu_short > 0 else 0.10
        drift_final = (mu_long * 0.40) + (mu_mid * (0.60 - weight_short)) + (mu_short * weight_short)
        kappa_base = 0.015 # Gravitasi lebih kuat di IDX untuk jaga RMSE
    else:
        # Untuk Saham Amerika: Dominasi momentum 1 tahun
        drift_final = (mu_long * 0.20) + (mu_mid * 0.80)
        kappa_base = 0.010 # Gravitasi lebih lemah di US agar bisa ikut rally
    
    # 3. DYNAMIC KAPPA (ELASTIC ANCHOR)
    # Jika harga di atas rata-rata dan tren naik, kendurkan tarikan ke bawah
    if last_p > sma_200 and mu_mid > 0:
        kappa = kappa_base * 0.5
    else:
        kappa = kappa_base
        
    # 4. VOLATILITY PROTECTION
    sigma = df.tail(126)['Close'].pct_change().std()
    
    rng = np.random.default_rng(42)
    sims = []
    
    for _ in range(30):
        path = [last_p]
        for t in range(days):
            # Log-gap distance ke SMA 200
            gap = np.log(sma_200) - np.log(path[-1])
            reversion_pull = kappa * gap
            
            # Stochastic Shock (GBM)
            shock = rng.normal(drift_final + reversion_pull, sigma)
            
            # Adaptive Projection Formula
            next_v = path[-1] * np.exp(shock - 0.5 * sigma**2)
            
            # Floor safety
            next_v = max(next_v, last_p * 0.30)
            path.append(next_v)
            
        sims.append(path[1:])
    
    # Menggunakan Median untuk stabilitas akurasi
    forecast = np.median(sims, axis=0)
    dates = [df['Date'].iloc[-1] + timedelta(days=i) for i in range(1, len(forecast)+1)]
    return {'dates': dates, 'forecast': forecast}

# ==========================================
# 4. SIDEBAR & DATABASE
# ==========================================
DB = {
    "🇮🇩 INDONESIA (IDX)": {
        "Banking": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK"],
        "Tech & Telco": ["GOTO.JK", "TLKM.JK", "BUKA.JK", "ISAT.JK"],
        "Energy & Mining": ["ADRO.JK", "ANTM.JK", "PTBA.JK", "MEDC.JK", "TINS.JK"],
        "Consumer & Retail": ["UNVR.JK", "ICBP.JK", "INDF.JK", "AMRT.JK"]
    },
    "🇺🇸 USA (WALL ST)": {
        "Magnificent 7": ["NVDA", "AAPL", "TSLA", "MSFT", "GOOGL", "META", "AMZN"],
        "Semiconductors": ["AMD", "TSM", "INTC", "AVGO", "MU"],
        "Financials": ["JPM", "GS", "BAC", "V", "MA"],
        "Consumer": ["KO", "PEP", "NKE", "SBUX", "WMT"]
    }
}

with st.sidebar:
    st.markdown('<div class="sidebar-brand">NIX<span>TRAD</span></div>', unsafe_allow_html=True)
    lang = st.radio("Lang", ["ID", "EN"], horizontal=True, label_visibility="collapsed")
    reg = st.selectbox("Region", list(DB.keys()))
    sec = st.selectbox("Sector", list(DB[reg].keys()))
    ticker = st.selectbox("Asset", DB[reg][sec])
    hrz = st.slider("Forecast Horizon (Months)", 1, 24, 12)
    st.markdown("---")
    m_txt, m_css = get_market_status(ticker)
    st.markdown(f'<div class="status-badge {m_css}">{m_txt}</div>', unsafe_allow_html=True)

# ==========================================
# 5. RENDER UI
# ==========================================
t = {
    "ID": {"price": "Harga Terakhir", "target": "Target AI", "upd": "Terakhir Update", "val": "Grafik Validasi"},
    "EN": {"price": "Last Price", "target": "AI Target", "upd": "Last Update", "val": "Validation Graph"}
}[lang]

df, last_upd = fetch_data(ticker)

if df is not None:
    sim = GOLDEN_Engine(df, ticker, hrz * 21)
    curr = float(df['Close'].iloc[-1])
    target = float(sim['forecast'][-1])
    roi = (target - curr) / curr
    c_roi = "#00ff88" if float(roi) > 0 else "#ff3355"

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["upd"]}</div><div style="font-size:1.1rem; font-weight:700; color:{c_roi}">{last_upd}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["price"]}</div><div class="metric-value">{format_currency(curr, ticker)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["target"]}</div><div class="metric-value" style="color:#00ff88">{format_currency(target, ticker)}</div><div style="color:{c_roi}; font-weight:700;">ROI: {roi:+.1%}</div></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📉 Terminal Analytics", f"🛡️ {t['val']}"])
    
    with tab1:
        fig = make_subplots(rows=1, cols=1)
        h = df.tail(500)
        fig.add_trace(go.Candlestick(x=h['Date'], open=h['Open'], high=h['High'], low=h['Low'], close=h['Close'], name='Market Price', increasing_line_color='#00ff88', decreasing_line_color='#ff3355'))
        fig.add_trace(go.Scatter(x=sim['dates'], y=sim['forecast'], name='AI Adaptive Path', line=dict(color='#0088ff', width=3, dash='dot')))
        fig.update_layout(template="plotly_dark", height=700, margin=dict(t=30,b=0,l=0,r=0), dragmode='pan', xaxis=dict(showgrid=False, rangeslider=dict(visible=False), type='date'), yaxis=dict(side='right', gridcolor='#111', zeroline=False), hovermode="x unified", showlegend=True)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    with tab2:
        test_d = 90
        train, test = df.iloc[:-test_d], df.iloc[-test_d:]
        bt = GOLDEN_Engine(train, ticker, test_d)
        if bt:
            m_l = min(len(test), len(bt['forecast']))
            rmse = np.sqrt(np.mean((test['Close'].values[:m_l] - bt['forecast'][:m_l])**2))
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=test['Date'], y=test['Close'], name='Real Market', line=dict(color='#fff', width=2.5)))
            fig_v.add_trace(go.Scatter(x=test['Date'], y=bt['forecast'], name='AI Prediction', line=dict(color='#0088ff', width=2.5, dash='dash')))
            fig_v.update_layout(template="plotly_dark", height=450, title=f"90-Day Backtest Analysis (RMSE: {rmse:.2f})", dragmode='pan', xaxis=dict(showgrid=False), yaxis=dict(gridcolor='#111', side='right'), hovermode="x unified")
            st.plotly_chart(fig_v, use_container_width=True, config={'scrollZoom': True})
            st.markdown(f'<div class="bento-card" style="text-align:center;">Reliability Score: <span style="color:#00ff88; font-weight:800;">{(1 - rmse/curr)*100:.1f}%</span></div>', unsafe_allow_html=True)
else:
    st.error("Market Feed Offline.")