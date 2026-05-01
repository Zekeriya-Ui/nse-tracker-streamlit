# 📈 NSE Tracker — Streamlit

A Streamlit-powered dashboard for the **Nairobi Securities Exchange (NSE)**, inspired by the [NSE Tracker Replit app](https://nairobi-exchange-stocks--zacharianyambu6.replit.app/).

## Features

- 📊 **Dashboard** — live index cards (NSE 20, 25, All, 10), market overview, top gainers/losers/active
- 📈 **Equities** — searchable stock table + interactive candlestick chart
- 🏭 **Sectors** — pie & bar charts for sector market cap and performance
- ⭐ **Watchlist** — add/remove stocks, comparative sparkline chart
- 📰 **News** — mock market news feed with ticker filter

## Run Locally

```bash
git clone https://github.com/Zekeriya-Ui/nse-tracker-streamlit.git
cd nse-tracker-streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Fork or push this repo to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select this repo → `app.py` → **Deploy**

## Tech Stack

| Tool | Purpose |
|------|---------|
| Streamlit | UI framework |
| Plotly | Interactive charts |
| Pandas | Data manipulation |

> **Note:** This version uses simulated/mock NSE data. For live data, integrate the [NSE Data API](https://afx.kwayisi.org/nseke/) or a web scraper targeting the NSE portal.
