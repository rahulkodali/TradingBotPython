
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
URL = "https://data.alpaca.markets/v2/stocks/bars"

class MarketDataFetcher:
    def __init__(self, headers):
        self.headers = headers

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
            "feed": "iex" ##change to sip after getting paid
        }

        response = requests.get(URL, headers=self.headers, params=params)
        response.raise_for_status()
        data = response.json()
        bars = data["bars"].get(symbol, [])
        df = pd.DataFrame(bars)
        if df.empty:
            return pd.DataFrame(columns=["c"])
        df["t"] = pd.to_datetime(df["t"])
        df.set_index("t", inplace=True)
        return df