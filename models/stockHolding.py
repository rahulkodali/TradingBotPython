import pandas as pd
from datetime import datetime, timedelta, timezone

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

    # def update_price(self, new_price: float):
    #     new_row = pd.DataFrame({"c": [new_price]}, index=[datetime.now(UTC)])
    #     self.df = pd.concat([self.df, new_row])
    #     self.ema21 = self.compute_ema(21)
    #     self.ema50 = self.compute_ema(50)