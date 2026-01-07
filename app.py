import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# CONFIG DASAR
st.set_page_config(page_title="NIXTRAD", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000; color: #fff; }
    .bento-card { background: #0a0a0a; border: 1px solid #1e1e1e; border-radius: 12px; padding: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# FETCH DATA DENGAN ERROR HANDLING KUAT
@st.cache_data(ttl=3600) # Simpan 1 jam biar gak kena blokir Yahoo
def fetch_data(ticker):
    try:
        df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.reset_index(inplace=True)
        return df
    except: return None

# SIDEBAR DATABASE
DB = {
    "🇮🇩 INDONESIA": ["BBCA.JK", "BBRI.JK", "TLKM.JK", "GOTO.JK", "ANTM.JK"],
    "🇺🇸 USA TECH": ["NVDA", "AAPL", "TSLA", "MSFT", "GOOGL"],
    "🪙 CRYPTO": ["BTC-USD", "ETH-USD", "SOL-USD"]
}

with st.sidebar:
    st.title("NIXTRAD")
    reg = st.selectbox("Region", list(DB.keys()))
    ticker = st.selectbox("Asset", DB[reg])

# RENDER UI
data = fetch_data(ticker)
if data is not None:
    curr = float(data['Close'].iloc[-1])
    
    st.markdown(f'<div class="bento-card">HARGA SAAT INI<br><h1>{curr:,.2f}</h1></div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], line=dict(color='#0088ff', width=2)))
    fig.update_layout(template="plotly_dark", height=500, margin=dict(t=20,b=20,l=0,r=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Yahoo Finance lagi sibuk/limit. Coba refresh atau ganti aset lain.")