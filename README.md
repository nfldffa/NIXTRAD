# 💹 NIXTRAD | GOLDEN STABLE V35.1

![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)
> **Terminal Riset Pasar dengan Akurasi Tinggi & Proyeksi Realitas AI.**

NIXTRAD adalah platform analisis instrumen keuangan interaktif yang menggabungkan visualisasi data real-time dengan **Golden Sentinel Engine**. Dirancang untuk memberikan proyeksi harga aset yang stabil dan terkalibrasi melalui pengujian RMSE (Root Mean Square Error).



## 🛠️ Tech Stack
* **Language:** Python 3.11+
* **Framework:** Streamlit
* **Data Source:** Yahoo Finance API
* **Visuals:** Plotly Interactive Subplots
* **Math:** NumPy (Monte Carlo Simulation & Z-Score Snap Force)

## 🚀 Fitur Unggulan
* **Golden Sentinel Engine:** Algoritma proyeksi yang diredam (*Low Variance*) untuk menjaga stabilitas akurasi jangka panjang.
* **Bento Grid Interface:** Tampilan metrik harga, target AI, dan ROI dalam desain grid modern.
* **90-Day Backtest Calibration:** Fitur validasi otomatis untuk menghitung nilai RMSE dan *Reliability Score* model.
* **Multi-Asset Support:** Saham IDX (Banking, Tech, Mining), Wall Street (Magnificent 7), dan Crypto Major.
* **Interactive Analytics:** Grafik Candlestick yang mendukung *Scroll Zoom* dan *Pan* untuk analisis mendalam.

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