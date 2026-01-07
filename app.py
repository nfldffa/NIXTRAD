import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# CONFIG
st.set_page_config(page_title="NIXTRAD SYMMETRIC", layout="wide")

# STYLING
st.markdown("""
<style>
    .stApp { background-color: #000; color: #fff; }
    .bento-card { 
        background: #0a0a0a; border: 1px solid #1e1e1e; border-radius: 12px; padding: 20px; 
        text-align: center; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        return df
    except: return None

def get_forecast(df, days):
    last_p = float(df['Close'].iloc[-1])
    rng = np.random.default_rng(42)
    path = [last_p]
    for _ in range(days):
        next_v = path[-1] * (1 + 0.0005 + rng.normal(0, 0.01))
        path.append(next_v)
    dates = [df['Date'].iloc[-1] + timedelta(days=i) for i in range(1, days+1)]
    return dates, path[1:]

# DATABASE
DB = {
    "🇮🇩 INDONESIA": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "GOTO.JK", "ANTM.JK"],
    "🇺🇸 USA TECH": ["NVDA", "AAPL", "TSLA", "MSFT", "GOOGL"],
    "🪙 CRYPTO": ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"]
}

with st.sidebar:
    st.title("NIXTRAD")
    reg = st.selectbox("Pilih Region", list(DB.keys()))
    ticker = st.selectbox("Pilih Aset", DB[reg])
    hrz = st.slider("Bulan", 1, 12, 6)

# RENDER
df = fetch_data(ticker)
if df is not None:
    dates, forecast = get_forecast(df, hrz * 21)
    curr, target = float(df['Close'].iloc[-1]), float(forecast[-1])
    roi = (target - curr) / curr
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="bento-card">HARGA<br><h3>{curr:,.2f}</h3></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="bento-card">TARGET<br><h3>{target:,.2f}</h3></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="bento-card">ROI<br><h3 style="color:{"#00ff88" if roi>0 else "#ff3355"}">{roi:+.1%}</h3></div>', unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'].tail(100), y=df['Close'].tail(100), name='History', line=dict(color='#fff')))
    fig.add_trace(go.Scatter(x=dates, y=forecast, name='Forecast', line=dict(color='#0088ff', dash='dot')))
    fig.update_layout(template="plotly_dark", height=450, margin=dict(t=10,b=10,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Gagal narik data. Yahoo Finance mungkin lagi limit IP server Streamlit. Tunggu 5 menit.")