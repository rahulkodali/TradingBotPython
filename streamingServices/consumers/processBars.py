from models.stockHolding import Position
from alpacaFunctions.updates.tradeExecutor import OrderType, createOrder
import redis
from managers.initializer import HEADERS
from alpacaFunctions.reads.marketData import fetchBars

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def updateEma(prevEma, price, span):
    alpha = 2 / (span + 1)
    return (price * alpha) + (prevEma * (1 - alpha))

def handleBarUpdates(symbol: str, price: float, timestamp: str):
    redisKey = f"position:{symbol}"
    tsKey = f"last_ts:{symbol}"

    # Prevent duplicate updates for the same bar
    if r.get(tsKey) == timestamp:
        print("Already processed this bar")
        return  # already processed this bar
    r.set(tsKey, timestamp)

    lock = r.lock(f"lock:{symbol}", timeout=5, blocking_timeout=2)
    if lock.acquire(blocking=True):
        try:
            data = r.hgetall(redisKey)

            prevEma21 = float(data["ema21"])
            prevEma50 = float(data["ema50"])
            ema21 = updateEma(prevEma21, price, 21)
            ema50 = updateEma(prevEma50, price, 50)

            df = fetchBars(HEADERS, symbol, "1Min", 5000)
            pandasEma21 = df["c"].ewm(21, adjust=False).mean().iloc[-1]
            pandasEma50 = df["c"].ewm(50, adjust=False).mean().iloc[-1]

            r.hset(redisKey, mapping={
                "ema21": float(pandasEma21),
                "ema50": float(pandasEma50)
            })

            print(f"{symbol}'s new EMA21: {ema21}")
            print(f"{symbol}'s new EMA50: {ema50}")
            print(f"Pandas {symbol}'s new EMA21: {pandasEma21}")
            print(f"Pandas {symbol}'s new EMA50: {pandasEma50}")

            ema21 = pandasEma21
            ema50 = pandasEma50
            
            if data["status"] == "SOLD" and ema21 > ema50:
                print(f"Golden Cross for {symbol}")
                createOrder(symbol, float(data["qty"]), OrderType.BUY)
                r.hset(redisKey, mapping={"status": "HOLDING"})

            elif data["status"] == "HOLDING" and ema21 < ema50:
                print(f"Death Cross for {symbol}")
                createOrder(symbol, float(data["qty"]), OrderType.SELL)
                r.hset(redisKey, mapping={"status": "SOLD"})

        finally:
            lock.release()
    else:
        print(f"[{symbol}] Skipping due to lock contention")

def consumeStream(symbol):
    stream = f"bar_stream:{symbol}"
    lastId = "0"
    while True:
        entries = r.xread({stream: lastId}, block=5000, count=10)
        for streamKey, msgs in entries:
            for msgId, data in msgs:
                price = float(data["price"])
                timestamp = data["timestamp"]
                handleBarUpdates(symbol, price, timestamp)
                lastId = msgId
