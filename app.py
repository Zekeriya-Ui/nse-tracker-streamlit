import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
import random
import time

st.set_page_config(
    page_title="NSE Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #fdf8f4; }
[data-testid="stSidebar"] { background-color: #fff; border-right: 1px solid #f0e8e0; }
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 4px solid #2ecc71;
    margin-bottom: 10px;
}
.metric-value { font-size: 1.8rem; font-weight: 700; color: #1a1a2e; }
.metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
.metric-change-pos { color: #2ecc71; font-weight: 600; }
.metric-change-neg { color: #e74c3c; font-weight: 600; }
.section-header {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 20px 0 10px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.nse-brand { color: #e8500a; font-weight: 800; font-size: 1.4rem; }
.status-closed {
    background: #f0f0f0;
    color: #666;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.status-open {
    background: #d4edda;
    color: #155724;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.watchlist-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
}
.ticker-symbol { font-weight: 700; font-size: 1rem; color: #1a1a2e; }
.ticker-name { font-size: 0.75rem; color: #999; }
.ticker-price { font-weight: 600; }
stframe { border: none; }
</style>
""", unsafe_allow_html=True)

# ── Mock NSE Data ────────────────────────────────────────────────────────────
NSE_STOCKS = {
    "SCOM": {"name": "Safaricom Plc", "price": 17.85, "change": 1.71, "volume": 12500000, "sector": "Telecommunication"},
    "EQTY": {"name": "Equity Group Holdings", "price": 48.95, "change": 1.77, "volume": 3200000, "sector": "Banking"},
    "KCB":  {"name": "KCB Group Plc", "price": 41.25, "change": 1.85, "volume": 2800000, "sector": "Banking"},
    "EABL": {"name": "East African Breweries", "price": 168.50, "change": -1.03, "volume": 450000, "sector": "Manufacturing"},
    "COOP": {"name": "Co-operative Bank", "price": 13.75, "change": 0.73, "volume": 1900000, "sector": "Banking"},
    "ABSA": {"name": "ABSA Bank Kenya", "price": 15.20, "change": 2.15, "volume": 1100000, "sector": "Banking"},
    "NCBA": {"name": "NCBA Group", "price": 44.00, "change": -0.45, "volume": 780000, "sector": "Banking"},
    "KQ":   {"name": "Kenya Airways Plc", "price": 4.85, "change": 4.98, "volume": 5600000, "sector": "Aviation"},
    "UCHM":{"name": "Uchumi Supermarkets", "price": 0.27, "change": 3.85, "volume": 320000, "sector": "Commercial"},
    "BAT":  {"name": "BAT Kenya", "price": 440.00, "change": -0.68, "volume": 25000, "sector": "Manufacturing"},
    "CARB": {"name": "Carbacid Investments", "price": 12.80, "change": 1.59, "volume": 230000, "sector": "Manufacturing"},
    "BRITAM":{"name":"Britam Holdings","price":6.22,"change":0.49,"volume":890000,"sector":"Insurance"},
    "JUB":  {"name": "Jubilee Holdings", "price": 195.00, "change": -0.51, "volume": 34000, "sector": "Insurance"},
    "KENGEN":{"name":"KenGen","price":4.46,"change":1.13,"volume":2300000,"sector":"Energy"},
    "KPLC": {"name": "Kenya Power", "price": 2.53, "change": -1.17, "volume": 1750000, "sector": "Energy"},
    "SASN": {"name": "Sasini Plc", "price": 21.50, "change": 2.38, "volume": 95000, "sector": "Agriculture"},
    "KAKZ": {"name": "Kakuzi Plc", "price": 375.00, "change": 0.00, "volume": 4500, "sector": "Agriculture"},
    "BAMB": {"name": "Bamburi Cement", "price": 50.25, "change": -1.37, "volume": 310000, "sector": "Manufacturing"},
    "CTUM": {"name": "Centum Investment", "price": 17.00, "change": 1.19, "volume": 420000, "sector": "Investment"},
    "NSE":  {"name": "Nairobi Securities Exchange", "price": 9.80, "change": 0.51, "volume": 145000, "sector": "Financial Services"},
}

INDICES = {
    "NSE 20":  {"value": 2168.45, "change": 0.77},
    "NSE 25":  {"value": 4112.78, "change": 0.85},
    "NSE All": {"value": 142.86,  "change": 1.02},
    "NSE 10":  {"value": 1492.55, "change": 0.78},
}

SECTOR_COLORS = {
    "Banking": "#2196F3", "Telecommunication": "#4CAF50", "Manufacturing": "#FF9800",
    "Energy": "#9C27B0", "Agriculture": "#8BC34A", "Insurance": "#00BCD4",
    "Aviation": "#F44336", "Commercial": "#FF5722", "Investment": "#607D8B",
    "Financial Services": "#795548",
}

def generate_sparkline(base, periods=30, volatility=0.015):
    prices = [base]
    for _ in range(periods - 1):
        prices.append(prices[-1] * (1 + random.gauss(0, volatility)))
    return prices

def make_sparkline(data, color="#2ecc71"):
    fig = go.Figure(go.Scatter(
        y=data, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.1)").replace("rgb", "rgba") if "rgb" in color else color + "1a"
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=60, paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

def make_price_chart(ticker, days=30):
    stock = NSE_STOCKS[ticker]
    base = stock["price"]
    dates = [datetime.now() - timedelta(days=days - i) for i in range(days)]
    prices = generate_sparkline(base, days, 0.02)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=dates,
        open=[p * random.uniform(0.99, 1.01) for p in prices],
        high=[p * random.uniform(1.005, 1.02) for p in prices],
        low=[p * random.uniform(0.98, 0.995) for p in prices],
        close=prices,
        name=ticker,
        increasing_line_color="#2ecc71",
        decreasing_line_color="#e74c3c"
    ))
    fig.update_layout(
        title=f"{ticker} – {stock['name']}",
        xaxis_title="Date", yaxis_title="Price (Ksh)",
        height=350, template="plotly_white",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_rangeslider_visible=False
    )
    return fig

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="nse-brand">📈 NSE Tracker</div>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigation", ["🏠 Dashboard", "📊 Equities", "🏭 Sectors", "⭐ Watchlist", "📰 News"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Market Data © Nairobi Securities Exchange")

page = page.split(" ", 1)[1]  # strip emoji

# ── DASHBOARD ────────────────────────────────────────────────────────────────
if page == "Dashboard":
    now = datetime.now()
    market_open = 9 <= now.hour < 15 and now.weekday() < 5
    status_cls  = "status-open" if market_open else "status-closed"
    status_txt  = "OPEN" if market_open else "CLOSED"

    st.markdown(
        f'<span class="{status_cls}">{status_txt}</span> '
        f'<b>NASI 142.86</b> <span class="metric-change-pos">▲ 1.02%</span>',
        unsafe_allow_html=True
    )
    st.markdown("")

    # Index cards
    cols = st.columns(4)
    for col, (name, idx) in zip(cols, INDICES.items()):
        clr = "#2ecc71" if idx["change"] >= 0 else "#e74c3c"
        sign = "+" if idx["change"] >= 0 else ""
        spark = generate_sparkline(idx["value"])
        with col:
            st.markdown(
                f'<div class="metric-card">'  
                f'<div class="metric-label">{name} Share Index</div>'
                f'<div class="metric-value">{idx["value"]:,.2f}</div>'
                f'<div style="color:{clr};font-weight:600">{sign}{idx["change"]}%</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.plotly_chart(make_sparkline(spark, clr), use_container_width=True, config={"displayModeBar": False})

    # Market Overview
    st.markdown('<div class="section-header">📊 Market Overview</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Equity Turnover",  "Ksh 1,058,009,063")
    c2.metric("Total Volume",     "48.8M")
    c3.metric("Market Cap",       "Ksh 1,973,512,372")
    c4.metric("Advancers / Decliners", "31 / 4")

    # Market Movers
    st.markdown('<div class="section-header">🚀 Market Movers</div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📈 Top Gainers", "📉 Top Losers", "🔥 Most Active"])

    df = pd.DataFrame([
        {"Ticker": t, "Company": v["name"], "Price (Ksh)": v["price"], "Change %": v["change"], "Volume": v["volume"]}
        for t, v in NSE_STOCKS.items()
    ])

    with tab1:
        gainers = df[df["Change %"] > 0].sort_values("Change %", ascending=False).head(10)
        st.dataframe(
            gainers.style.format({"Price (Ksh)": "{:.2f}", "Change %": "+{:.2f}%", "Volume": "{:,.0f}"})
                   .applymap(lambda _: "color: #2ecc71", subset=["Change %"]),
            use_container_width=True, hide_index=True
        )
    with tab2:
        losers = df[df["Change %"] < 0].sort_values("Change %").head(10)
        st.dataframe(
            losers.style.format({"Price (Ksh)": "{:.2f}", "Change %": "{:.2f}%", "Volume": "{:,.0f}"})
                  .applymap(lambda _: "color: #e74c3c", subset=["Change %"]),
            use_container_width=True, hide_index=True
        )
    with tab3:
        active = df.sort_values("Volume", ascending=False).head(10)
        st.dataframe(
            active.style.format({"Price (Ksh)": "{:.2f}", "Change %": "{:+.2f}%", "Volume": "{:,.0f}"}),
            use_container_width=True, hide_index=True
        )

# ── EQUITIES ─────────────────────────────────────────────────────────────────
elif page == "Equities":
    st.title("📊 Equities")
    search = st.text_input("🔍 Search ticker or company…", placeholder="e.g. SCOM or Safaricom")

    df = pd.DataFrame([
        {"Ticker": t, "Company": v["name"], "Sector": v["sector"],
         "Price (Ksh)": v["price"], "Change %": v["change"], "Volume": v["volume"]}
        for t, v in NSE_STOCKS.items()
    ])

    if search:
        df = df[df["Ticker"].str.contains(search.upper()) | df["Company"].str.contains(search, case=False)]

    def color_change(val):
        return "color: #2ecc71" if val > 0 else ("color: #e74c3c" if val < 0 else "")

    st.dataframe(
        df.style.format({"Price (Ksh)": "{:.2f}", "Change %": "{:+.2f}%", "Volume": "{:,.0f}"})
               .applymap(color_change, subset=["Change %"]),
        use_container_width=True, hide_index=True, height=500
    )

    st.markdown("---")
    st.subheader("📈 Price Chart")
    selected = st.selectbox("Select a stock", list(NSE_STOCKS.keys()),
                            format_func=lambda t: f"{t} – {NSE_STOCKS[t]['name']}")
    period = st.slider("Days", 7, 180, 30)
    st.plotly_chart(make_price_chart(selected, period), use_container_width=True)

# ── SECTORS ──────────────────────────────────────────────────────────────────
elif page == "Sectors":
    st.title("🏭 Sectors")

    sector_df = pd.DataFrame([
        {"Sector": v["sector"], "Market Cap": v["price"] * v["volume"],
         "Avg Change %": v["change"], "Stocks": 1}
        for v in NSE_STOCKS.values()
    ]).groupby("Sector").agg(
        {"Market Cap": "sum", "Avg Change %": "mean", "Stocks": "sum"}
    ).reset_index()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(sector_df, values="Market Cap", names="Sector",
                     title="Market Cap by Sector",
                     color="Sector", color_discrete_map=SECTOR_COLORS,
                     hole=0.4)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(sector_df.sort_values("Avg Change %"),
                      x="Avg Change %", y="Sector", orientation="h",
                      title="Avg % Change by Sector",
                      color="Avg Change %",
                      color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"])
        fig2.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        sector_df.style.format({"Market Cap": "Ksh {:,.0f}", "Avg Change %": "{:+.2f}%", "Stocks": "{:.0f}"}),
        use_container_width=True, hide_index=True
    )

# ── WATCHLIST ────────────────────────────────────────────────────────────────
elif page == "Watchlist":
    st.title("⭐ Watchlist")

    if "watchlist" not in st.session_state:
        st.session_state.watchlist = ["SCOM", "EQTY", "KCB", "EABL"]

    add_ticker = st.selectbox("Add to watchlist", [t for t in NSE_STOCKS if t not in st.session_state.watchlist])
    if st.button("➕ Add"):
        st.session_state.watchlist.append(add_ticker)
        st.rerun()

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add stocks above.")
    else:
        for ticker in st.session_state.watchlist:
            s = NSE_STOCKS[ticker]
            clr = "#2ecc71" if s["change"] >= 0 else "#e74c3c"
            sign = "+" if s["change"] >= 0 else ""
            c1, c2, c3, c4 = st.columns([2, 3, 2, 1])
            c1.markdown(f"**{ticker}**")
            c2.caption(s["name"])
            c3.markdown(f'<span style="color:{clr}">Ksh {s["price"]:,.2f} ({sign}{s["change"]}%)</span>', unsafe_allow_html=True)
            if c4.button("✕", key=f"del_{ticker}"):
                st.session_state.watchlist.remove(ticker)
                st.rerun()

    if st.session_state.watchlist:
        st.markdown("---")
        wl_data = {t: generate_sparkline(NSE_STOCKS[t]["price"]) for t in st.session_state.watchlist}
        fig = go.Figure()
        for t, prices in wl_data.items():
            fig.add_trace(go.Scatter(y=prices, mode="lines", name=t))
        fig.update_layout(title="Watchlist Performance (relative)", height=300, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

# ── NEWS ─────────────────────────────────────────────────────────────────────
elif page == "News":
    st.title("📰 Market News")
    news_items = [
        {"title": "Safaricom posts strong Q1 results, M-Pesa revenue up 18%",
         "source": "Business Daily", "time": "2 hours ago", "ticker": "SCOM",
         "summary": "Safaricom Plc reported a significant jump in M-Pesa revenues in Q1 2026, driven by increased mobile money transactions across East Africa."},
        {"title": "KCB Group completes acquisition of regional bank, eyes Uganda expansion",
         "source": "The Standard", "time": "4 hours ago", "ticker": "KCB",
         "summary": "KCB Group Plc has finalized a strategic acquisition of a mid-tier regional bank, strengthening its presence across the East African Community."},
        {"title": "Kenya Airways receives new Boeing 787 Dreamliner, resumes long-haul routes",
         "source": "Nation Africa", "time": "6 hours ago", "ticker": "KQ",
         "summary": "Kenya Airways took delivery of a new Boeing 787-9 Dreamliner, enabling resumption of direct Nairobi–New York and Nairobi–London routes."},
        {"title": "East African Breweries launches new premium spirits line",
         "source": "Reuters", "time": "8 hours ago", "ticker": "EABL",
         "summary": "EABL unveiled its new premium spirits portfolio targeting the growing middle-class consumer segment across East Africa."},
        {"title": "NSE All Share Index hits 5-month high amid foreign investor inflows",
         "source": "Capital FM", "time": "10 hours ago", "ticker": "NSE",
         "summary": "The NSE All Share Index (NASI) climbed to a 5-month high as foreign institutional investors increased their holdings in Kenyan equities."},
        {"title": "Equity Group reports record profits, declares Ksh 4.00 dividend",
         "source": "Business Daily", "time": "12 hours ago", "ticker": "EQTY",
         "summary": "Equity Group Holdings recorded record full-year profits and declared a Ksh 4.00 per share dividend, rewarding shareholders."},
    ]
    filter_ticker = st.selectbox("Filter by ticker", ["All"] + list(NSE_STOCKS.keys()))
    for item in news_items:
        if filter_ticker != "All" and item["ticker"] != filter_ticker:
            continue
        with st.expander(f"📰 {item['title']}"):
            st.caption(f"**{item['source']}** · {item['time']} · `{item['ticker']}`")
            st.write(item["summary"])
