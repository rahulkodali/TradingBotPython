from models.stockHolding import Position
from alpacaFunctions.updates.tradeExecutor import OrderType, createOrder
import redis


r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def updateEma(prevEma, price, span):
    alpha = 2 / (span + 1)
    return (price * alpha) + (prevEma * (1 - alpha))

def handleBarUpdates(symbol: str, price: float):
        
        lock = r.lock(f"lock:{symbol}", timeout=5, blocking_timeout=2)
        if lock.acquire(blocking = True):
            try:   
                redisKey = f"position:{symbol}"
                data = r.hgetall(redisKey)

                prevEma21 = float(data["ema21"])
                prevEma50 = float(data["ema50"])
                ema21 = updateEma(prevEma21, price, 21)
                ema50 = updateEma(prevEma50, price, 50)

                # Check for cross
                if data["status"] == "SOLD" and ema21 > ema50:
                    print(f"Golden Cross for {symbol}")
                    createOrder(symbol, float(data["qty"]), OrderType.BUY)
                    r.hset(redisKey, mapping={
                        "status": "HOLDING"
                    })
                elif data["status"] == "HOLDING" and ema21 < ema50:
                    print(f"Death Cross for {symbol}")
                    createOrder(symbol, float(data["qty"]), OrderType.SELL)
                    r.hset(redisKey, mapping={
                        "status": "SOLD"
                    })
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
                handleBarUpdates(symbol, price)
                lastId = msgId