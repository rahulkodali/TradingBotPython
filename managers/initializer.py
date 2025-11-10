import os, requests, redis
from datetime import timezone

from models.stockHolding import StockHolding
from alpacaFunctions.reads.marketData import fetchBars
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

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def initialize():
    # 0. Delete everything in Redis stream/pipeline
    streamKeys = r.keys("bar_stream:*")
    if streamKeys:
        r.delete(*streamKeys)
        print(f"[INIT] Cleared {len(streamKeys)} bar_streams.")
    
    # 1. If Redis is empty, load from Alpaca
    if len(r.keys("position:*")) == 0:
        print("[Init] Redis empty — pulling positions from Alpaca...")

        response = requests.get(POSITIONS_URL, headers=HEADERS)
        response.raise_for_status()
        alpaca_positions = response.json()

        positions = [
            {
                "symbol": pos["symbol"],
                "qty": float(pos["qty"]),
            }
            for pos in alpaca_positions
        ]

    else:
        print("[Init] Redis contains previous state — restoring symbols...")

        # Redis already has stored positions, so restore from Redis keys
        symbols = [key.split(":")[1] for key in r.keys("position:*")]

        positions = []
        for sym in symbols:
            stored = r.hgetall(f"position:{sym}")
            positions.append({
                "symbol": sym,
                "qty": float(stored.get("qty", 0)),
                "status": stored.get("status", "HOLDING")
            })

    # Refresh EMAs for all positions
    for pos in positions:
        symbol = pos["symbol"]
        qty = float(pos.get("qty", 0))
        status = pos.get("status", "HOLDING")

        df = fetchBars(HEADERS, symbol, "1Min", 1000)
        if df.empty:
            print(f"[Init] Skipping {symbol} — no data")
            continue

        stock = StockHolding(symbol, qty, df)

        r.hset(
            f"position:{symbol}",
            mapping={
                "qty": qty,
                "status": status,
                "ema21": float(stock.ema21),
                "ema50": float(stock.ema50),
            }
        )

        print(f"[{symbol}] qty={qty}, status={status}, EMA21={stock.ema21:.2f}, EMA50={stock.ema50:.2f}")
