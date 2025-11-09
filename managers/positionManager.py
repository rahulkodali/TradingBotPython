import os
import requests
import pandas as pd
from datetime import timezone
from typing import Dict

from models.stockHolding import StockHolding
from alpacaFunctions.reads.marketData import MarketDataFetcher
from alpacaFunctions.updates.tradeExecutor import TradeExecutor, OrderType
# from dotenv import load_dotenv

# load_dotenv()

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
UTC = timezone.utc
HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_API_KEY,
    "accept": "application/json",
    "content-type": "application/json"
}

BASE_BAR_URL = "https://data.alpaca.markets/v2/stocks/bars"
POSITIONS_URL = "https://paper-api.alpaca.markets/v2/positions"

class PositionManager:
    def __init__(self):
        self.positions: Dict[str, StockHolding] = {}
        self.fetcher = MarketDataFetcher(HEADERS)
        self.executor = TradeExecutor(HEADERS)

    def initialize(self):
        response = requests.get(POSITIONS_URL, headers=HEADERS)
        response.raise_for_status()
        values = response.json()

        for position in values:
            symbol = position['symbol']
            qty = float(position['qty'])
            df = self.fetcher.fetchBars(symbol, "1Day", 100)
            if not df.empty:
                self.positions[symbol] = StockHolding(symbol, qty, df)

        for sym, p in self.positions.items():
            print(f"{sym}: qty = {p.qty}, EMA21 = {p.ema21:.2f}, EMA50 = {p.ema50:.2f}")