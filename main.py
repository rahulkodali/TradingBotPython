import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from typing import Dict
# from dotenv import load_dotenv

# load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_API_KEY,
    "accept": "application/json"
}

BASE_BAR_URL = "https://data.alpaca.markets/v2/stocks/bars"
POSITIONS_URL = "https://paper-api.alpaca.markets/v2/positions"

UTC = timezone.utc


class StockHolding:
    def __init__(self, symbol: str, qty: float, df: pd.DataFrame):
        self.symbol = symbol
        self.qty = qty
        self.df = df
        self.ema21 = self.compute_ema(21)
        self.ema50 = self.compute_ema(50)

    def compute_ema(self, span: int) -> float:
        return self.df["c"].ewm(span=span, adjust=False).mean().iloc[-1]

    def update_price(self, new_price: float):
        new_row = pd.DataFrame({"c": [new_price]}, index=[datetime.now(UTC)])
        self.df = pd.concat([self.df, new_row])
        self.ema21 = self.compute_ema(21)
        self.ema50 = self.compute_ema(50)


class TradingManager:
    def __init__(self):
        self.positions: Dict[str, StockHolding] = {}
        self.initialize()

    def fetch_bars(self, symbol: str, timeframe: str = "1Day", limit: int = 500):
        end = datetime.now(UTC)
        start = end - timedelta(days=5)
        params = {
            "symbols": symbol,
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "adjustment": "raw",
            "feed": "iex"
        }

        response = requests.get(BASE_BAR_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        bars = data["bars"].get(symbol, [])
        df = pd.DataFrame(bars)
        if df.empty:
            return pd.DataFrame(columns=["c"])
        df["t"] = pd.to_datetime(df["t"])
        df.set_index("t", inplace=True)
        return df

    def initialize(self):
        response = requests.get(POSITIONS_URL, headers=HEADERS)
        response.raise_for_status()
        values = response.json()

        for position in values:
            symbol = position['symbol']
            qty = float(position['qty'])
            df = self.fetch_bars(symbol, "1Day", 100)
            if not df.empty:
                self.positions[symbol] = StockHolding(symbol, qty, df)

        for sym, p in self.positions.items():
            print(f"{sym}: qty = {p.qty}, EMA21 = {p.ema21:.2f}, EMA50 = {p.ema50:.2f}")


if __name__ == "__main__":
    bot = TradingManager()
