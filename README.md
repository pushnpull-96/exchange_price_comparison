# exchange_price_comparison

A Python script that connects to multiple cryptocurrency exchanges to compare live prices and find arbitrage opportunities.

## 🔍 What It Does

- Connects to public APIs for Binance, Coinbase, Kraken, Bitstamp, Gemini, and OKX.
- Fetches **live bid/ask prices** for assets like BTC/USD, ETH/USD, and more.
- Compares prices across exchanges and calculates **spreads**.
- Identifies **arbitrage opportunities** after subtracting estimated exchange fees.
- Optionally plots **Coinbase mid prices over time**.
- Logs profitable arbitrage opportunities to a CSV file with timestamps.

## ✅ Features

- Price comparison tables with colored spread indicators.
- Arbitrage scanner (net of fees).
- CSV export of profitable trades.
- Basic price history tracking + matplotlib charting.
- Easy to extend with new assets or exchanges.

## 🛠 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 How to run

```bash 
python price_comparison.py
```

This will:
1. Print price comparison tables for all supported assets.
2. Track and optionally plot price history (Coinbase).
3. Print and log arbitrage opportunities to arb_opportunities.csv.

## 📁 Output Example

```bash
🚀 BTC/USD Price Comparison
+-----------+--------------+-------------+----------+
| Exchange  | Buy (Ask)    | Sell (Bid)  | Spread   |
+-----------+--------------+-------------+----------+
| Binance   | 85,300.00000 | 85,290.00000| 10.0000  |
...

📈 Net Arbitrage Opportunities (after fees)
+----------+----------+-----------+---------+-----------+---------+-------------+
| Asset    | Buy @    | Ask       | Sell @  | Bid       | Net $   | Net Spread |
+----------+----------+-----------+---------+-----------+---------+-------------+
| BTC/USD  | Kraken   | 85,200.00 | Coinbase| 85,500.00 | 200.00  | 198.70      |
...
```

## 🤓 Customize

You can add assets or modify exchange symbols via the ASSET_EXCHANGE_MAP at the top of the script:

```python
ASSET_EXCHANGE_MAP = {
    "BTC/USD": {
        "Binance": "BTCUSDT",
        "Coinbase": "BTC-USD",
        ...
    }
}
```