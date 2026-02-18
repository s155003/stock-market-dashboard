import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")


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

INDICES = {
    "S&P 500":  "^GSPC",
    "NASDAQ":   "^IXIC",
    "Dow Jones":"^DJI",
    "VIX":      "^VIX",
}

SECTORS = {
    "Technology":   "XLK",
    "Healthcare":   "XLV",
    "Financials":   "XLF",
    "Energy":       "XLE",
    "Consumer":     "XLY",
    "Industrials":  "XLI",
    "Utilities":    "XLU",
    "Real Estate":  "XLRE",
}

PERIOD_1Y   = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
PERIOD_3M   = (datetime.today() - timedelta(days=90)).strftime("%Y-%m-%d")
TODAY       = datetime.today().strftime("%Y-%m-%d")

GREEN   = "#2ca02c"
RED     = "#d62728"
BLUE    = "#1f77b4"
GRAY    = "#7f7f7f"
GOLD    = "#ff7f0e"
BG      = "#0d1117"
PANEL   = "#161b22"
TEXT    = "#e6edf3"
MUTED   = "#8b949e"


def fetch_ticker(ticker, start, end=TODAY):
    try:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def fetch_quote(ticker):
    try:
        t    = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period="2d")
        if len(hist) < 2:
            return None
        prev  = float(hist["Close"].iloc[-2])
        curr  = float(hist["Close"].iloc[-1])
        chg   = curr - prev
        chg_p = (chg / prev) * 100
        return {
            "price":   curr,
            "change":  chg,
            "pct":     chg_p,
            "volume":  hist["Volume"].iloc[-1],
            "high":    float(hist["High"].iloc[-1]),
            "low":     float(hist["Low"].iloc[-1]),
            "name":    info.get("shortName", ticker),
        }
    except Exception:
        return None


def add_indicators(df):
    close         = df["Close"].squeeze()
    df            = df.copy()
    df["MA20"]    = close.rolling(20).mean()
    df["MA50"]    = close.rolling(50).mean()
    df["EMA12"]   = close.ewm(span=12).mean()
    df["EMA26"]   = close.ewm(span=26).mean()
    df["MACD"]    = df["EMA12"] - df["EMA26"]
    df["Signal"]  = df["MACD"].ewm(span=9).mean()
    df["BB_mid"]  = close.rolling(20).mean()
    df["BB_std"]  = close.rolling(20).std()
    df["BB_up"]   = df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lo"]   = df["BB_mid"] - 2 * df["BB_std"]
    delta         = close.diff()
    gain          = delta.clip(lower=0).rolling(14).mean()
    loss          = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"]     = 100 - (100 / (1 + gain / (loss + 1e-6)))
    df["Volume_MA"] = df["Volume"].squeeze().rolling(20).mean()
    return df


def style_ax(ax, title="", ylabel=""):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.spines[:].set_color("#30363d")
    if title:
        ax.set_title(title, color=TEXT, fontsize=9, fontweight="bold", pad=6)
    if ylabel:
        ax.set_ylabel(ylabel, color=MUTED, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")


def plot_scorecard(ax, name, quote):
    ax.set_facecolor(PANEL)
    ax.spines[:].set_color("#30363d")
    ax.set_xticks([])
    ax.set_yticks([])

    if quote is None:
        ax.text(0.5, 0.5, "N/A", transform=ax.transAxes,
                ha="center", va="center", color=MUTED, fontsize=10)
        return

    color  = GREEN if quote["change"] >= 0 else RED
    arrow  = "▲" if quote["change"] >= 0 else "▼"
    symbol = f"{arrow} {abs(quote['pct']):.2f}%"

    ax.text(0.5, 0.80, name,        transform=ax.transAxes, ha="center", color=MUTED,  fontsize=7)
    ax.text(0.5, 0.52, f"${quote['price']:,.2f}", transform=ax.transAxes,
            ha="center", color=TEXT, fontsize=11, fontweight="bold")
    ax.text(0.5, 0.24, symbol,      transform=ax.transAxes, ha="center", color=color,  fontsize=9)


def build_dashboard():
    print("Fetching market data...")

    quotes     = {}
    idx_quotes = {}

    for name, ticker in WATCHLIST.items():
        print(f"  {ticker}...")
        quotes[name] = fetch_quote(ticker)

    for name, ticker in INDICES.items():
        print(f"  {ticker}...")
        idx_quotes[name] = fetch_quote(ticker)

    print("  Fetching historical data...")
    spy_hist   = fetch_ticker("SPY",  PERIOD_1Y)
    aapl_hist  = fetch_ticker("AAPL", PERIOD_3M)
    tsla_hist  = fetch_ticker("TSLA", PERIOD_3M)
    nvda_hist  = fetch_ticker("NVDA", PERIOD_3M)

    sector_perf = {}
    for name, ticker in SECTORS.items():
        df = fetch_ticker(ticker, PERIOD_3M)
        if df is not None and len(df) > 1:
            start_p = float(df["Close"].iloc[0])
            end_p   = float(df["Close"].iloc[-1])
            sector_perf[name] = (end_p - start_p) / start_p * 100

    print("Building dashboard...")

    plt.rcParams.update({
        "figure.facecolor":  BG,
        "text.color":        TEXT,
        "font.family":       "monospace",
    })

    fig = plt.figure(figsize=(24, 18))
    fig.patch.set_facecolor(BG)

    now_str = datetime.now().strftime("%B %d, %Y  %H:%M")
    fig.suptitle(f"STOCK MARKET DASHBOARD  |  {now_str}",
                 fontsize=15, fontweight="bold", color=TEXT, y=0.98)

    gs = gridspec.GridSpec(
        5, 8,
        figure=fig,
        hspace=0.55,
        wspace=0.4,
        top=0.94,
        bottom=0.04,
        left=0.05,
        right=0.97,
    )

    ax_sp   = fig.add_subplot(gs[0, :3])
    ax_rsi  = fig.add_subplot(gs[1, :3])
    ax_macd = fig.add_subplot(gs[2, :3])

    if spy_hist is not None:
        spy = add_indicators(spy_hist)
        close = spy["Close"].squeeze()
        dates = spy.index

        ax_sp.plot(dates, close,        color=BLUE,  linewidth=1.5, label="SPY Close")
        ax_sp.plot(dates, spy["MA20"],  color=GOLD,  linewidth=0.8, linestyle="--", label="MA20", alpha=0.8)
        ax_sp.plot(dates, spy["MA50"],  color=RED,   linewidth=0.8, linestyle="--", label="MA50", alpha=0.8)
        ax_sp.fill_between(dates, spy["BB_up"], spy["BB_lo"], alpha=0.08, color=BLUE)
        ax_sp.set_facecolor(PANEL)
        ax_sp.tick_params(colors=MUTED, labelsize=8)
        ax_sp.spines[:].set_color("#30363d")
        ax_sp.set_title("S&P 500 ETF (SPY) — 1 Year", color=TEXT, fontsize=9, fontweight="bold")
        ax_sp.set_ylabel("Price ($)", color=MUTED, fontsize=8)
        ax_sp.legend(fontsize=7, facecolor=PANEL, edgecolor="#30363d", labelcolor=TEXT)
        ax_sp.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_sp.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax_sp.xaxis.get_majorticklabels(), rotation=30, ha="right")

        ax_rsi.plot(dates, spy["RSI"], color=GOLD, linewidth=1)
        ax_rsi.axhline(70, color=RED,   linestyle="--", linewidth=0.8, alpha=0.7)
        ax_rsi.axhline(30, color=GREEN, linestyle="--", linewidth=0.8, alpha=0.7)
        ax_rsi.fill_between(dates, spy["RSI"], 70, where=spy["RSI"] >= 70, alpha=0.2, color=RED)
        ax_rsi.fill_between(dates, spy["RSI"], 30, where=spy["RSI"] <= 30, alpha=0.2, color=GREEN)
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_facecolor(PANEL)
        ax_rsi.tick_params(colors=MUTED, labelsize=8)
        ax_rsi.spines[:].set_color("#30363d")
        ax_rsi.set_title("RSI (14)", color=TEXT, fontsize=9, fontweight="bold")
        ax_rsi.set_ylabel("RSI", color=MUTED, fontsize=8)
        ax_rsi.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_rsi.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax_rsi.xaxis.get_majorticklabels(), rotation=30, ha="right")

        macd_col = [GREEN if v >= 0 else RED for v in (spy["MACD"] - spy["Signal"])]
        ax_macd.bar(dates, spy["MACD"] - spy["Signal"], color=macd_col, alpha=0.6, width=1.5)
        ax_macd.plot(dates, spy["MACD"],   color=BLUE, linewidth=1,   label="MACD")
        ax_macd.plot(dates, spy["Signal"], color=RED,  linewidth=0.8, label="Signal", linestyle="--")
        ax_macd.set_facecolor(PANEL)
        ax_macd.tick_params(colors=MUTED, labelsize=8)
        ax_macd.spines[:].set_color("#30363d")
        ax_macd.set_title("MACD", color=TEXT, fontsize=9, fontweight="bold")
        ax_macd.legend(fontsize=7, facecolor=PANEL, edgecolor="#30363d", labelcolor=TEXT)
        ax_macd.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_macd.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax_macd.xaxis.get_majorticklabels(), rotation=30, ha="right")

    idx_names = list(INDICES.keys())
    for i, (name, ticker) in enumerate(INDICES.items()):
        ax = fig.add_subplot(gs[0, 3 + i])
        plot_scorecard(ax, name, idx_quotes.get(name))

    stock_names = list(WATCHLIST.keys())
    for i, name in enumerate(stock_names[:4]):
        ax = fig.add_subplot(gs[1, 4 + i])
        plot_scorecard(ax, name, quotes.get(name))

    for i, name in enumerate(stock_names[4:]):
        ax = fig.add_subplot(gs[2, 4 + i])
        plot_scorecard(ax, name, quotes.get(name))

    ax_sector = fig.add_subplot(gs[3, :4])
    if sector_perf:
        names  = list(sector_perf.keys())
        values = list(sector_perf.values())
        colors = [GREEN if v >= 0 else RED for v in values]
        sorted_pairs = sorted(zip(values, names, colors))
        values, names, colors = zip(*sorted_pairs)
        bars = ax_sector.barh(names, values, color=colors, alpha=0.85, height=0.6)
        ax_sector.axvline(0, color=MUTED, linewidth=1)
        ax_sector.set_facecolor(PANEL)
        ax_sector.tick_params(colors=MUTED, labelsize=8)
        ax_sector.spines[:].set_color("#30363d")
        ax_sector.set_title("Sector Performance — 3 Months (%)", color=TEXT, fontsize=9, fontweight="bold")
        for bar, val in zip(bars, values):
            ax_sector.text(val + (0.1 if val >= 0 else -0.1), bar.get_y() + bar.get_height() / 2,
                           f"{val:+.1f}%", va="center",
                           ha="left" if val >= 0 else "right",
                           color=TEXT, fontsize=7)

    stock_pairs = [("AAPL", aapl_hist), ("TSLA", tsla_hist), ("NVDA", nvda_hist)]
    col_starts  = [4, 6, 4]

    for idx2, (ticker, hist) in enumerate(stock_pairs[:2]):
        ax = fig.add_subplot(gs[3, 4 + idx2 * 2: 4 + idx2 * 2 + 2])
        if hist is not None:
            df2   = add_indicators(hist)
            close = df2["Close"].squeeze()
            dates = df2.index
            color = GREEN if float(close.iloc[-1]) >= float(close.iloc[0]) else RED
            ax.plot(dates, close,         color=color, linewidth=1.5)
            ax.plot(dates, df2["MA20"],   color=GOLD,  linewidth=0.8, linestyle="--", alpha=0.7)
            ax.fill_between(dates, df2["BB_up"], df2["BB_lo"], alpha=0.08, color=color)
            ax.set_facecolor(PANEL)
            ax.tick_params(colors=MUTED, labelsize=7)
            ax.spines[:].set_color("#30363d")
            ax.set_title(f"{ticker} — 3M", color=TEXT, fontsize=9, fontweight="bold")
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")

    ax_nvda = fig.add_subplot(gs[4, :4])
    if nvda_hist is not None:
        df2   = add_indicators(nvda_hist)
        close = df2["Close"].squeeze()
        dates = df2.index
        color = GREEN if float(close.iloc[-1]) >= float(close.iloc[0]) else RED
        ax_nvda.plot(dates, close,       color=color, linewidth=1.5, label="NVDA")
        ax_nvda.plot(dates, df2["MA20"], color=GOLD,  linewidth=0.8, linestyle="--", label="MA20", alpha=0.7)
        ax_nvda.fill_between(dates, df2["BB_up"], df2["BB_lo"], alpha=0.08, color=color)
        ax_nvda.set_facecolor(PANEL)
        ax_nvda.tick_params(colors=MUTED, labelsize=8)
        ax_nvda.spines[:].set_color("#30363d")
        ax_nvda.set_title("NVDA — 3 Months with Bollinger Bands", color=TEXT, fontsize=9, fontweight="bold")
        ax_nvda.legend(fontsize=7, facecolor=PANEL, edgecolor="#30363d", labelcolor=TEXT)
        ax_nvda.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_nvda.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax_nvda.xaxis.get_majorticklabels(), rotation=30, ha="right")

    ax_vol = fig.add_subplot(gs[4, 4:])
    winners = {k: v for k, v in quotes.items() if v is not None}
    if winners:
        names  = list(winners.keys())
        pcts   = [winners[n]["pct"] for n in names]
        colors = [GREEN if p >= 0 else RED for p in pcts]
        sorted_pairs = sorted(zip(pcts, names, colors))
        pcts, names, colors = zip(*sorted_pairs)
        bars = ax_vol.barh(names, pcts, color=colors, alpha=0.85, height=0.6)
        ax_vol.axvline(0, color=MUTED, linewidth=1)
        ax_vol.set_facecolor(PANEL)
        ax_vol.tick_params(colors=MUTED, labelsize=8)
        ax_vol.spines[:].set_color("#30363d")
        ax_vol.set_title("Watchlist Daily Change (%)", color=TEXT, fontsize=9, fontweight="bold")
        for bar, val in zip(bars, pcts):
            ax_vol.text(val + (0.02 if val >= 0 else -0.02),
                        bar.get_y() + bar.get_height() / 2,
                        f"{val:+.2f}%", va="center",
                        ha="left" if val >= 0 else "right",
                        color=TEXT, fontsize=7)

    plt.savefig("stock_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor=BG, edgecolor="none")
    print("Dashboard saved as stock_dashboard.png")
    plt.show()


build_dashboard()
