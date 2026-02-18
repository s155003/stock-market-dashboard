# Stock Market Dashboard — Data Visualization

A Python data visualization project that pulls live stock market data from Yahoo Finance and renders a dark-themed, multi-panel dashboard covering indices, individual stocks, technical indicators, sector performance, and a customizable watchlist. Everything is generated in a single script and saved as a high-resolution PNG.

---

## Overview

Rather than checking five different websites to get a complete picture of the market, this dashboard pulls everything into one place. It fetches real-time quotes, calculates technical indicators, and lays out a comprehensive market overview in a single image — styled with a dark GitHub-inspired color scheme.

---

## What's on the Dashboard

### Top Left — SPY 1-Year Chart
The S&P 500 ETF (SPY) plotted over the past year with:
- 20-day and 50-day simple moving averages
- Bollinger Bands (20-day, 2 standard deviations)

### Middle Left — RSI Indicator
14-period Relative Strength Index for SPY with:
- Overbought zone (above 70) highlighted in red
- Oversold zone (below 30) highlighted in green

### Bottom Left — MACD
Moving Average Convergence Divergence for SPY with:
- MACD line and signal line
- Histogram bars colored green (bullish) or red (bearish)

### Top Right — Index Scorecards
Live price and daily percentage change for:
- S&P 500
- NASDAQ
- Dow Jones
- VIX (Volatility Index)

### Middle Right — Watchlist Scorecards
Live price and daily change for 8 stocks:
- Apple (AAPL)
- Microsoft (MSFT)
- NVIDIA (NVDA)
- Amazon (AMZN)
- Google (GOOGL)
- Tesla (TSLA)
- Meta (META)
- Netflix (NFLX)

### Sector Performance
Horizontal bar chart showing 3-month percentage returns for 8 S&P 500 sector ETFs:
- Technology (XLK)
- Healthcare (XLV)
- Financials (XLF)
- Energy (XLE)
- Consumer Discretionary (XLY)
- Industrials (XLI)
- Utilities (XLU)
- Real Estate (XLRE)

### Individual Stock Charts
3-month price charts with MA20 and Bollinger Bands for:
- Apple (AAPL)
- Tesla (TSLA)
- NVIDIA (NVDA)

### Watchlist Daily Change
Ranked horizontal bar chart of all watchlist stocks sorted by daily percentage change — green for gainers, red for losers.

---

## Technical Indicators Calculated

| Indicator | Formula | Use |
|---|---|---|
| MA20 | 20-day simple moving average | Short-term trend |
| MA50 | 50-day simple moving average | Medium-term trend |
| EMA12 / EMA26 | Exponential moving averages | MACD inputs |
| MACD | EMA12 − EMA26 | Momentum signal |
| Signal | 9-day EMA of MACD | MACD crossover trigger |
| RSI | 14-period relative strength | Overbought/oversold |
| BB_upper / BB_lower | 20-day MA ± 2 standard deviations | Volatility bands |

---

## Requirements

```
numpy
pandas
matplotlib
yfinance
```

Install all dependencies:

```bash
pip install numpy pandas matplotlib yfinance
```

---

## Usage

```bash
python stock_dashboard.py
```

The script fetches all data, builds the dashboard, displays it, and saves it as `stock_dashboard.png` in the same directory.

---

## Customization

### Change the watchlist
Edit the `WATCHLIST` dictionary at the top of the script:

```python
WATCHLIST = {
    "Apple":     "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA":    "NVDA",
    "Amazon":    "AMZN",
    "Google":    "GOOGL",
    "Tesla":     "TSLA",
    "Meta":      "META",
    "Netflix":   "NFLX",
}
```

Replace any entry with any valid Yahoo Finance ticker — crypto tickers like `BTC-USD` work too.

### Change the date ranges
```python
PERIOD_1Y = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
PERIOD_3M = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")
```

Adjust `days=365` or `days=90` to widen or narrow the chart windows.

### Change the color scheme
All colors are defined at the top of the script:

```python
GREEN = "#2ca02c"
RED   = "#d62728"
BLUE  = "#1f77b4"
GRAY  = "#7f7f7f"
GOLD  = "#ff7f0e"
BG    = "#0d1117"
PANEL = "#161b22"
TEXT  = "#e6edf3"
MUTED = "#8b949e"
```

---

## Example Terminal Output

```
Fetching market data...
  AAPL...
  MSFT...
  NVDA...
  AMZN...
  GOOGL...
  TSLA...
  META...
  NFLX...
  ^GSPC...
  ^IXIC...
  ^DJI...
  ^VIX...
  Fetching historical data...
Building dashboard...
Dashboard saved as stock_dashboard.png
```

---

## Extending the Project

- **Add crypto** — include BTC-USD, ETH-USD in the watchlist alongside equities
- **Schedule it daily** — use Python's `schedule` library or a cron job to regenerate the dashboard every morning before market open
- **Email delivery** — use `smtplib` to automatically email the PNG to yourself each day
- **Interactive version** — rewrite using `plotly` and `dash` to build a live, interactive web dashboard with hover tooltips and dropdowns
- **Add earnings calendar** — pull upcoming earnings dates and annotate them on individual stock charts
- **Portfolio tracker** — add a panel showing your personal holdings, cost basis, and unrealized P&L
