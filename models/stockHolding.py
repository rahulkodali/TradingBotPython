import pandas as pd
from datetime import datetime, timedelta, timezone
from enum import Enum

class Position(Enum):
    HOLDING = "HOLDING"
    SOLD = "SOLD"

UTC = timezone.utc

class StockHolding:
    def __init__(self, symbol: str, qty: float, df: pd.DataFrame):
        self.symbol = symbol
        self.qty = qty
        self.df = df
        self.ema21 = self.computeEma(21)
        self.ema50 = self.computeEma(50)
        self.status = Position.HOLDING

    def computeEma(self, span: int) -> float:
        return self.df["c"].ewm(span=span, adjust=False).mean().iloc[-1]