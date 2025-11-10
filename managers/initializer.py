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

redis = redis.Redis(host="localhost", port=6379, decode_responses=True)

def initialize():
    response = requests.get(POSITIONS_URL, headers=HEADERS)
    response.raise_for_status()
    values = response.json()

    for position in values:
        symbol = position['symbol']
        qty = float(position['qty'])
        # todo - maybe hardcode bars so even sold positions persist across days, 
        # we can use fetchBars to update HOLDING positions
        df = fetchBars(HEADERS, symbol, "1Day", 100)
        if df.empty:
            continue

        stock = StockHolding(symbol, qty, df)

        # Store in Redis
        redis.hmset(f"position:{symbol}", {
            "qty": stock.qty,
            "ema21": float(stock.ema21),
            "ema50": float(stock.ema50),
            "status": "HOLDING"  
        })

        print(f"[{symbol}] qty = {stock.qty}, EMA21 = {stock.ema21:.2f}, EMA50 = {stock.ema50:.2f}")