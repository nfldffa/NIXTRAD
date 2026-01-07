import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# ==========================================
# 1. NIXTRAD SYMMETRIC
# ==========================================
st.set_page_config(
    page_title="NIXTRAD SYMMETRIC",
    layout="wide",
    page_icon="💹",
    initial_sidebar_state="expanded"
)

# Kunci Seed agar konsisten 100%
np.random.seed(42)
random.seed(42)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    :root {
        --bg-color: #000000;
        --card-bg: #0a0a0a;
        --border-color: #1a1a1a;
        --bull-color: #00ff88;
        --bear-color: #ff3355;
        --accent-color: #0088ff;
    }

    .stApp {
        background-color: var(--bg-color);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #050505 !important;
        border-right: 1px solid var(--border-color) !important;
    }

    .bento-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 24px;
        height: 100%;
        transition: 0.3s;
    }
    .bento-card:hover { border-color: #333; }

    .metric-title { color: #666; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 800; line-height: 1; }
    
    .ai-insight {
        background: linear-gradient(90deg, rgba(0, 136, 255, 0.1) 0%, rgba(0,0,0,0) 100%);
        border-left: 3px solid var(--accent-color);
        padding: 16px; margin: 20px 0; font-size: 0.9rem; color: #ccc;
    }

    .ticker-wrap { width: 100%; overflow: hidden; background: #050505; border-bottom: 1px solid #111; padding: 10px 0; }
    .ticker { display: inline-block; white-space: nowrap; animation: ticker 60s linear infinite; }
    .ticker-item { display: inline-block; padding: 0 2rem; font-family: 'JetBrains Mono'; font-size: 0.8rem; }
    @keyframes ticker { 0% { transform: translateX(0); } 100% { transform: translateX(-100%); } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ASSET DATABASE
# ==========================================
ASSET_DB = {
    "🇮🇩 INDONESIA": {
        "Banking": {"BBCA.JK": "Bank BCA", "BBRI.JK": "Bank BRI", "BMRI.JK": "Bank Mandiri"},
        "Technology": {"GOTO.JK": "GoTo Tokopedia", "TLKM.JK": "Telkom Indonesia"},
        "Mining & Energy": {"ADRO.JK": "Adaro Energy", "ANTM.JK": "Aneka Tambang"}
    },
    "🇺🇸 UNITED STATES": {
        "Magnificent 7": {"NVDA": "NVIDIA", "AAPL": "Apple", "TSLA": "Tesla", "MSFT": "Microsoft", "GOOGL": "Google"},
        "Semiconductors": {"AMD": "AMD", "TSM": "TSMC"}
    },
    "🪙 CRYPTO & GLOBAL": {
        "Mainstream": {"BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "SOL-USD": "Solana"},
        "Commodities": {"GC=F": "Gold (Emas)", "CL=F": "Crude Oil"}
    }
}

# ==========================================
# 3. STABLE SENTINEL ENGINE (LOGIKA ASLI UNTOUCHED)
# ==========================================
@st.cache_data(ttl=300)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="10y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        df['SMA_200'] = df['Close'].rolling(200).mean()
        df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
        df['Z_Score'] = (df['Close'] - df['Close'].rolling(50).mean()) / df['Close'].rolling(50).std()
        
        return df.dropna()
    except: return None

def GOLDEN_Sentinel_Engine(df, ticker, forecast_days):
    try:
        # Pake float() biar ga error pas deploy
        last_price = float(df['Close'].iloc[-1])
        current_sma200 = float(df['SMA_200'].iloc[-1])
        current_z = float(df['Z_Score'].iloc[-1])
        
        daily_growth = 0.00048 if ".JK" in ticker else 0.0007
        gravity = 0.00015
        snap_force = 0.0004
        
        rng = np.random.default_rng(42)
        all_sims = []
        for _ in range(10):
            path = [last_price]
            for t in range(forecast_days):
                pull = (current_sma200 - path[-1]) / path[-1] * gravity
                noise = rng.normal(0, 0.005)
                decay = np.exp(-t/1000)
                next_val = path[-1] * (1 + (daily_growth + pull - (snap_force * current_z) + noise) * decay)
                path.append(next_val)
            all_sims.append(path[1:])
            
        forecast = np.median(all_sims, axis=0)
        dates = [df['Date'].iloc[-1] + timedelta(days=i) for i in range(1, len(forecast)+1)]
        return {'dates': dates, 'forecast': forecast}
    except: return None

# ==========================================
# 4. UI RENDER
# ==========================================
st.markdown("""<div class="ticker-wrap"><div class="ticker">
    <span class="ticker-item" style="color:#00ff88">BBCA.JK 10,250 ▲ 0.8%</span>
    <span class="ticker-item" style="color:#ff3355">BTC/USD $96,120 ▼ 0.4%</span>
    <span class="ticker-item" style="color:#00ff88">NVDA $142.10 ▲ 2.4%</span>
    <span class="ticker-item" style="color:#ffffff">XAU/USD $2,680 ▬ 0.0%</span>
</div></div>""", unsafe_allow_html=True)

c_brand, c_l = st.columns([8, 2])
with c_brand: st.markdown("<h1 style='margin:0; font-weight:800; letter-spacing:-2px;'>NIX<span style='color:#00ff88'>TRAD</span> GOLDEN</h1>", unsafe_allow_html=True)
with c_l: lang = st.selectbox("", ["ID", "EN"], label_visibility="collapsed")

st.markdown("---")

with st.sidebar:
    st.markdown("<p style='color:#666; font-size:0.75rem; font-weight:700;'>MARKET NAVIGATOR</p>", unsafe_allow_html=True)
    region = st.selectbox("Region", list(ASSET_DB.keys()))
    sector = st.selectbox("Sector", list(ASSET_DB[region].keys()))
    ticker = st.selectbox("Asset", list(ASSET_DB[region][sector].keys()), format_func=lambda x: f"{x} - {ASSET_DB[region][sector][x]}")
    horizon_months = st.slider("Horizon (Months)", 1, 24, 12)

df = fetch_data(ticker)
if df is not None:
    forecast_days = horizon_months * 21
    sim = GOLDEN_Sentinel_Engine(df, ticker, forecast_days)
    
    if sim:
        curr, target = float(df['Close'].iloc[-1]), float(sim['forecast'][-1])
        roi = (target - curr) / curr
        c = "#00ff88" if roi > 0 else "#ff3355"

        m1, m2, m3 = st.columns([2, 1, 1])
        with m1: st.markdown(f'<div class="bento-card"><div class="metric-title">{ticker} Market Insight</div><div class="metric-value">{ticker}</div><div style="color:{c}; font-weight:800; background:rgba(0,255,136,0.1); padding:4px 10px; border-radius:4px; display:inline-block; margin-top:10px;">{"BULLISH" if roi>0 else "BEARISH"}</div></div>', unsafe_allow_html=True)
        with m2: st.markdown(f'<div class="bento-card"><div class="metric-title">Last Price</div><div class="metric-value">{curr:,.2f}</div></div>', unsafe_allow_html=True)
        with m3: st.markdown(f'<div class="bento-card"><div class="metric-title">AI Target</div><div class="metric-value" style="color:{c}">{target:,.2f}</div><div style="font-size:0.8rem; color:#666;">ROI: {roi:+.1%}</div></div>', unsafe_allow_html=True)

        t1, t2 = st.tabs(["📉 ANALYTICS", "🛡️ VALIDATION"])
        
        with t1:
            fig = go.Figure()
            h_df = df.tail(350)
            fig.add_trace(go.Candlestick(x=h_df['Date'], open=h_df['Open'], high=h_df['High'], low=h_df['Low'], close=h_df['Close'], name='Market', increasing_line_color='#00ff88', decreasing_line_color='#ff3355'))
            fig.add_trace(go.Scatter(x=sim['dates'], y=sim['forecast'], name='AI Reality Path', line=dict(color='#0088ff', width=3, dash='dot')))
            fig.update_layout(template="plotly_dark", height=700, margin=dict(t=30, b=0, l=0, r=0), dragmode='pan', xaxis=dict(showgrid=False, rangeslider=dict(visible=False)), yaxis=dict(gridcolor='#111', side='right'), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

        with t2:
            days_bt = 90
            train, test = df.iloc[:-days_bt], df.iloc[-days_bt:]
            bt = GOLDEN_Sentinel_Engine(train, ticker, days_bt)
            if bt:
                m_l = min(len(test), len(bt['forecast']))
                rmse = np.sqrt(np.mean((test['Close'].values[:m_l] - bt['forecast'][:m_l])**2))
                
                # --- GRAFIK VALIDASI (DIBUAT INTERAKTIF) ---
                fig_v = go.Figure()
                fig_v.add_trace(go.Scatter(x=test['Date'], y=test['Close'], name='Real Market', line=dict(color='#ffffff', width=2.5)))
                fig_v.add_trace(go.Scatter(x=test['Date'], y=bt['forecast'], name='AI Prediction', line=dict(color='#0088ff', width=2.5, dash='dash')))
                
                fig_v.update_layout(
                    template="plotly_dark", 
                    height=500, 
                    margin=dict(t=50, b=10, l=0, r=0),
                    dragmode='pan', # Biar bisa digeser
                    title=f"90-Day Backtest Analysis (RMSE: {rmse:.2f})",
                    xaxis=dict(showgrid=False, type='date'), 
                    yaxis=dict(gridcolor='#111', side='right'),
                    hovermode="x unified",
                    showlegend=True
                )
                # Pake scrollZoom: True biar bisa di-zoom pake mouse wheel
                st.plotly_chart(fig_v, use_container_width=True, config={'scrollZoom': True})
                
                st.markdown(f'<div class="bento-card" style="text-align:center;">Model Confidence Score: <span style="color:#00ff88; font-weight:800;">{(1 - rmse/curr)*100:.1f}%</span></div>', unsafe_allow_html=True)
else:
    st.error("Market Feed Offline.")