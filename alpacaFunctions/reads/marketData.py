
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

UTC = timezone.utc
URL = "https://data.alpaca.markets/v2/stocks/bars"

def fetchBars(headers, symbol: str, timeframe: str = "1Day", limit: int = 500):
    end = datetime.now(UTC)
    start = end - timedelta(days=5)
    params = {
        "symbols": symbol,
        "timeframe": timeframe,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "limit": limit,
        "adjustment": "raw",
        "feed": "iex" ##change to sip after getting paid tier
    }

    response = requests.get(URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    bars = data["bars"].get(symbol, [])
    df = pd.DataFrame(bars)
    if df.empty:
        return pd.DataFrame(columns=["c"])
    df["t"] = pd.to_datetime(df["t"])
    df.set_index("t", inplace=True)
    return df