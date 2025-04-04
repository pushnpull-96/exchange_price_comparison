import requests
import matplotlib.pyplot as plt
from collections import defaultdict
import datetime
import time
from tabulate import tabulate
from colorama import Fore, Style, init

import csv

init()

# Central asset-to-exchange map
ASSET_EXCHANGE_MAP = {
    "BTC/USD": {
        "Binance": "BTCUSDT",
        "Coinbase": "BTC-USD",
        "Kraken": "XBTUSD",
        "Bitstamp": "btcusd",
        "Gemini": "btcusd",
        "OKX": "BTC-USDT"
    },
    "ETH/USD": {
        "Binance": "ETHUSDT",
        "Coinbase": "ETH-USD",
        "Kraken": "ETHUSD",
        "Bitstamp": "ethusd",
        "Gemini": "ethusd",
        "OKX": "ETH-USDT"
    },
    "SOL/USD": {
        "Binance": "SOLUSDT",
        "Coinbase": "SOL-USD",
        "Kraken": "SOLUSD",
        "OKX": "SOL-USDT"
    },
    "ADA/USD": {
        "Binance": "ADAUSDT",
        "Coinbase": "ADA-USD",
        "Kraken": "ADAUSD",
        "OKX": "ADA-USDT"
    },
    "XRP/USD": {
        "Binance": "XRPUSDT",
        "Coinbase": "XRP-USD",
        "Kraken": "XRPUSD",
        "Bitstamp": "xrpusd",
        "OKX": "XRP-USDT"
    }
}

EXCHANGE_FEES = {
    "Binance": 0.001,
    "Coinbase": 0.0015,
    "Kraken": 0.002,
    "Bitstamp": 0.005,
    "Gemini": 0.003,
    "OKX": 0.001
}


def fetch_price(exchange, symbol):
    try:
        if exchange == "Binance":
            r = requests.get(f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}").json()
            return float(r["askPrice"]), float(r["bidPrice"])
        elif exchange == "Coinbase":
            r = requests.get(f"https://api.exchange.coinbase.com/products/{symbol}/book?level=1").json()
            return float(r["asks"][0][0]), float(r["bids"][0][0])
        elif exchange == "Kraken":
            r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={symbol}").json()
            data = list(r["result"].values())[0]
            return float(data["a"][0]), float(data["b"][0])
        elif exchange == "Bitstamp":
            r = requests.get(f"https://www.bitstamp.net/api/v2/ticker/{symbol}").json()
            return float(r["ask"]), float(r["bid"])
        elif exchange == "Gemini":
            r = requests.get(f"https://api.gemini.com/v1/pubticker/{symbol}").json()
            return float(r["ask"]), float(r["bid"])
        elif exchange == "OKX":
            r = requests.get(f"https://www.okx.com/api/v5/market/ticker?instId={symbol}").json()
            data = r["data"][0]
            return float(data["askPx"]), float(data["bidPx"])
    except:
        return float("nan"), float("nan")

def color_spread(spread):
    if spread < 0.1:
        return Fore.GREEN + f"{spread:.4f}" + Style.RESET_ALL
    elif spread < 1:
        return Fore.YELLOW + f"{spread:.4f}" + Style.RESET_ALL
    return Fore.RED + f"{spread:.4f}" + Style.RESET_ALL

def compare_asset_prices(asset):
    prices = []
    for exchange, symbol in ASSET_EXCHANGE_MAP.get(asset, {}).items():
        ask, bid = fetch_price(exchange, symbol)
        if not (ask != ask or bid != bid):  # NaN check
            spread = ask - bid
            
            prices.append([
                exchange,
                f"{ask:,.5f}",
                f"{bid:,.5f}",
                color_spread(spread)
            ])
    print(f"\n🚀 {Style.BRIGHT}{asset}{Style.RESET_ALL} Price Comparison")
    print(tabulate(prices, headers=["Exchange", "Buy (Ask)", "Sell (Bid)", "Spread"], tablefmt="fancy_grid"))

def find_arbitrage_opportunities(assets):
    print(f"\n{Style.BRIGHT}📈 Net Arbitrage Opportunities (after fees):{Style.RESET_ALL}")
    rows = []
    for asset in assets:
        data = []
        for exchange, symbol in ASSET_EXCHANGE_MAP.get(asset, {}).items():
            ask, bid = fetch_price(exchange, symbol)
            if not (ask != ask or bid != bid):
                data.append((exchange, ask, bid))

        if not data:
            continue

        buy_exchange, lowest_ask, _ = min(data, key=lambda x: x[1])
        sell_exchange, _, highest_bid = max(data, key=lambda x: x[2])

        buy_fee = EXCHANGE_FEES.get(buy_exchange, 0)
        sell_fee = EXCHANGE_FEES.get(sell_exchange, 0)
        gross_spread = highest_bid - lowest_ask
        fee_cost = (lowest_ask * buy_fee) + (highest_bid * sell_fee)
        net_profit = gross_spread - fee_cost

        if net_profit > 0:
            rows.append([asset,buy_exchange,f"{lowest_ask:,.4f}",sell_exchange,f"{highest_bid:,.4f}",f"{net_profit:,.4f}",color_spread(net_profit)])
        log_opportunity_to_csv(asset, buy_exchange, lowest_ask, sell_exchange, highest_bid, net_profit)

    if rows:
        print(tabulate(rows, headers=["Asset", "Buy @", "Ask", "Sell @", "Bid", "Net $", "Net Spread"], tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "No net arbitrage opportunities found." + Style.RESET_ALL)



# Price history tracker
price_history = defaultdict(list)

def update_price_history():
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    for asset in ["BTC/USD", "ETH/USD"]:
        coinbase = ASSET_EXCHANGE_MAP[asset].get("Coinbase")
        if coinbase:
            ask, bid = fetch_price("Coinbase", coinbase)
            mid = (ask + bid) / 2 if ask == ask and bid == bid else None
            if mid:
                price_history[asset].append((timestamp, mid))

def plot_price_history():
    for asset, entries in price_history.items():
        if not entries:
            continue
        times, prices = zip(*entries)
        plt.figure(figsize=(10, 4))
        plt.plot(times, prices, marker='o', label=asset)
        plt.title(f"{asset} - Coinbase Mid Price")
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

def log_opportunity_to_csv(asset, buy_ex, ask, sell_ex, bid, net_profit):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("arb_opportunities.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, asset, buy_ex, ask, sell_ex, bid, net_profit])

if __name__ == "__main__":
    # Price tables
    for asset in ASSET_EXCHANGE_MAP:
        compare_asset_prices(asset)
    # Price Data    
    for _ in range(5):  # Collect 5 time points
        update_price_history()
        time.sleep(5)

    print(list(ASSET_EXCHANGE_MAP.keys()))
    find_arbitrage_opportunities(list(ASSET_EXCHANGE_MAP.keys())
)