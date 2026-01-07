# 💹 NIXTRAD SYMMETRIC

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://nixtrad-symmetric.streamlit.app/)
> **Terminal Riset Pasar dengan Akurasi Tinggi & Proyeksi Realitas AI.**

NIXTRAD adalah platform analisis instrumen keuangan interaktif yang menggabungkan visualisasi data real-time dengan **Region-Adaptive Engine**. Dirancang untuk memberikan proyeksi harga aset yang stabil dan terkalibrasi melalui pengujian RMSE (Root Mean Square Error).

## 🛠️ Tech Stack
* **Language:** Python 3.11+
* **Framework:** Streamlit
* **Data Source:** Yahoo Finance API
* **Visuals:** Plotly Interactive Subplots
* **Math:** NumPy (Monte Carlo Simulation & Dynamic Mean Reversion)

## 🚀 Fitur Unggulan
* **Region-Adaptive Engine:** Algoritma cerdas yang secara otomatis menyesuaikan insting momentum berdasarkan wilayah pasar (IDX vs Wall Street).
* **Bento Grid Interface:** Tampilan metrik harga, target AI, dan ROI dalam desain grid modern yang responsif.
* **90-Day Backtest Calibration:** Fitur validasi otomatis untuk menghitung nilai RMSE dan *Reliability Score* berdasarkan performa historis.
* **Perfect Instinct Logic:** Integrasi *Fractal Momentum* yang mempertimbangkan akselerasi harga jangka pendek tanpa melupakan fondasi tren jangka panjang.
* **Interactive Analytics:** Grafik Candlestick bertenaga Plotly yang mendukung *Scroll Zoom* dan *Pan* untuk analisis teknikal mendalam.

## 📈 Cara Menjalankan Secara Lokal
1.  **Clone Repository:**
    ```bash
    git clone [https://github.com/nfldffa/NIXTRAD.git](https://github.com/nfldffa/NIXTRAD.git)
    cd NIXTRAD
    ```
2.  **Setup Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate  # Mac/Linux
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Launch App:**
    ```bash
    streamlit run app.py
    ```

## ⚠️ Disclaimer
Aplikasi ini dibuat untuk tujuan riset dan edukasi. Proyeksi AI didasarkan pada data historis dan tidak menjamin keuntungan di masa depan. *Always do your own research.*

---
**Developed with ❤️ by [Naufal Daffa Erlangga](https://github.com/nfldffa)**