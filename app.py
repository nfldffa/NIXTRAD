import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz

# ==========================================
# 1. CONFIG & SYMMETRIC STYLING
# ==========================================
st.set_page_config(page_title="NIXTRAD SYMMETRIC", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    :root { --bg: #000; --card: #0a0a0a; --bull: #00ff88; --bear: #ff3355; --accent: #0088ff; }
    
    .stApp { background-color: var(--bg); color: #fff; font-family: 'Inter', sans-serif; }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1e1e1e !important; }
    .sidebar-brand { font-size: 2.2rem; font-weight: 800; letter-spacing: -2px; color: #fff; text-align: center; padding: 20px 0; border-bottom: 1px solid #1e1e1e; }
    .sidebar-brand span { color: var(--bull); }

    /* BENTO BOX SYMMETRIC */
    .bento-card { 
        background: var(--card); 
        border: 1px solid #1e1e1e; 
        border-radius: 12px; 
        padding: 20px; 
        height: 120px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        transition: 0.3s;
    }
    .bento-card:hover { border-color: #333; background: #0f0f0f; }
    
    .metric-title { color: #666; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-bottom: 8px; letter-spacing: 1px; }
    .metric-value { font-family: 'JetBrains Mono'; font-size: 1.6rem; font-weight: 800; line-height: 1.2; }
    
    .status-badge { padding: 5px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; display: inline-block; }
    .open { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .closed { background: rgba(255, 51, 85, 0.1); color: #ff3355; border: 1px solid #ff3355; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CORE UTILITIES
# ==========================================
def get_market_status(ticker):
    if "-USD" in ticker: return "LIVE 24/7", "open"
    if "=F" in ticker or "=X" in ticker: return "MARKET ACTIVE", "open"
    
    tz = pytz.timezone('Asia/Jakarta' if ".JK" in ticker or "^JKSE" in ticker else 'US/Eastern')
    now = datetime.now(tz)
    if now.weekday() < 5 and 9 <= now.hour < 16: return "OPEN", "open"
    return "CLOSED", "closed"

def format_currency(value, ticker):
    if ".JK" in ticker or "^JKSE" in ticker:
        return f"Rp {value:,.0f}"
    return f"${value:,.2f}"

@st.cache_data(ttl=600)
def fetch_data(ticker):
    try:
        # Pake yf.download biar stabil di server Streamlit
        df = yf.download(ticker, period="5y", interval="1d", auto_adjust=True, progress=False)
        
        if df is None or df.empty:
            return None, None
            
        # Fix MultiIndex yfinance terbaru
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df.reset_index(inplace=True)
        
        # Kalkulasi Indikator
        df['SMA_200'] = df['Close'].rolling(200).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        df['RSI'] = 100 - (100 / (1 + rs))
        
        upd = df['Date'].iloc[-1].strftime("%d %b %Y")
        return df.dropna(), upd
    except Exception:
        return None, None

def ENGINE(df, ticker, days):
    # FORCE FLOAT: Biar gak error 'ambiguous truth value' pas deploy
    last_p = float(df['Close'].iloc[-1])
    sma_200 = float(df['SMA_200'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    
    is_indo = ".JK" in ticker or "^JKSE" in ticker
    growth = 0.00045 if is_indo else 0.0006 
    
    if rsi > 75: growth -= 0.0009
    elif rsi < 30: growth += 0.0005
    
    gravity = 0.00018
    rng = np.random.default_rng(42)
    sims = []
    
    for _ in range(15):
        path = [last_p]
        for t in range(days):
            pull = (sma_200 - path[-1]) / path[-1] * gravity
            noise = rng.normal(0, 0.004) 
            next_v = path[-1] * (1 + growth + pull + noise)
            path.append(next_v)
        sims.append(path[1:])
        
    forecast = np.median(sims, axis=0)
    dates = [df['Date'].iloc[-1] + timedelta(days=i) for i in range(1, len(forecast)+1)]
    return {'dates': dates, 'forecast': forecast}

# ==========================================
# 3. DATABASE PRODUK (LENGKAP)
# ==========================================
DB = {
    "🇮🇩 INDONESIA STOCKS": [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK", 
        "GOTO.JK", "ANTM.JK", "ADRO.JK", "UNVR.JK", "AMRT.JK"
    ],
    "🇺🇸 USA TECH": [
        "NVDA", "AAPL", "TSLA", "MSFT", "GOOGL", 
        "AMD", "META", "AMZN", "NFLX", "INTC"
    ],
    "🪙 CRYPTO CURRENCY": [
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
        "ADA-USD", "DOGE-USD", "DOT-USD", "MATIC-USD"
    ]
}

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">NIX<span>TRAD</span></div>', unsafe_allow_html=True)
    lang = st.radio("Language", ["ID", "EN"], horizontal=True, label_visibility="collapsed")
    reg = st.selectbox("Category", list(DB.keys()))
    ticker = st.selectbox("Asset", DB[reg])
    hrz = st.slider("Horizon (Months)", 1, 24, 12)
    st.markdown("---")
    m_txt, m_css = get_market_status(ticker)
    st.markdown(f'<div class="status-badge {m_css}">{m_txt}</div>', unsafe_allow_html=True)

# ==========================================
# 5. RENDER UI
# ==========================================
t = {
    "ID": {"upd": "Update", "price": "Harga", "target": "Target", "roi": "ROI", "val": "Validasi"},
    "EN": {"upd": "Update", "price": "Price", "target": "Target", "roi": "ROI", "val": "Validation"}
}[lang]

df, last_upd = fetch_data(ticker)

if df is not None and not df.empty:
    sim = ENGINE(df, ticker, hrz * 21)
    
    # KONVERSI FLOAT (FIX DEPLOY)
    curr = float(df['Close'].iloc[-1])
    target = float(sim['forecast'][-1])
    roi = float((target - curr) / curr)
    
    c_roi = "#00ff88" if roi > 0 else "#ff3355"

    # SYMMETRIC GRID
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["upd"]}</div><div class="metric-value" style="font-size:1.1rem;">{last_upd}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["price"]}</div><div class="metric-value">{format_currency(curr, ticker)}</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["target"]}</div><div class="metric-value" style="color:{c_roi}">{format_currency(target, ticker)}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="bento-card"><div class="metric-title">{t["roi"]}</div><div class="metric-value" style="color:{c_roi}">{roi:+.1%}</div></div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📉 Terminal Analytics", f"🛡️ {t['val']}"])
    
    with tab1:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
        h = df.tail(400)
        fig.add_trace(go.Candlestick(x=h['Date'], open=h['Open'], high=h['High'], low=h['Low'], close=h['Close'], name='Market', increasing_line_color='#00ff88', decreasing_line_color='#ff3355'), row=1, col=1)
        fig.add_trace(go.Scatter(x=sim['dates'], y=sim['forecast'], name='NIXTRAD Path', line=dict(color='#0088ff', width=3, dash='dot')), row=1, col=1)
        
        v_colors = ['#00ff88' if float(r['Close']) >= float(r['Open']) else '#ff3355' for _, r in h.iterrows()]
        fig.add_trace(go.Bar(x=h['Date'], y=h['Volume'], marker_color=v_colors, opacity=0.6, name='Volume'), row=2, col=1)
        
        fig.update_layout(template="plotly_dark", height=750, margin=dict(t=10,b=10,l=0,r=0), dragmode='pan', showlegend=False, xaxis2=dict(showgrid=False), yaxis=dict(side='right', gridcolor='#111'), yaxis2=dict(side='right', gridcolor='#111'))
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})

    with tab2:
        test_d = 90
        train, test = df.iloc[:-test_d], df.iloc[-test_d:]
        bt = ENGINE(train, ticker, test_d)
        if bt:
            fig_v = go.Figure()
            fig_v.add_trace(go.Scatter(x=test['Date'], y=test['Close'], name='Real Market Price', line=dict(color='#fff', width=2.5)))
            fig_v.add_trace(go.Scatter(x=test['Date'], y=bt['forecast'], name='Proyeksi', line=dict(color='#0088ff', dash='dash', width=2)))
            fig_v.update_layout(template="plotly_dark", height=500, title="90-Day Backtest Analysis", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(showgrid=False), yaxis=dict(side='right', gridcolor='#111'))
            st.plotly_chart(fig_v, use_container_width=True)
            
            rmse = np.sqrt(np.mean((test['Close'].values - bt['forecast'][:len(test)])**2))
            st.markdown(f'<div class="bento-card" style="height:auto; margin-top:20px;">RMSE: {rmse:.2f} | Reliability: {(1 - rmse/curr)*100:.1f}%</div>', unsafe_allow_html=True)
else:
    st.error("Data Feed Offline atau Terkena Rate Limit. Silakan coba lagi nanti.")