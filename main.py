import asyncio, redis, time, threading
from threading import Thread
from streamingServices.consumers.processBars import consumeStream
from streamingServices.producers.streamBars import streamBars
from managers.initializer import initialize
# from datetime import datetime, timezone

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def main():
    print("[Init] Initializing positions...")
    
    if len(r.keys("position:*")) == 0:
        initialize()  # this loads positions from Alpaca and writes to Redis

    print("[Stream] Starting consumers for each symbol...")
    symbols = [key.split(":")[1] for key in r.keys("position:*")]

    for symbol in symbols:
        t = Thread(target=consumeStream, args=(symbol,))
        t.daemon = True
        t.start()


    ##testing - redis-cli flushall before
    # time.sleep(1)

    # print("[Test] Publishing fake bars to test consumers...")
    # now = datetime.now(timezone.utc).isoformat()
    # r.xadd("bar_stream:AAPL", {"symbol": "AAPL", "price": "5000", "timestamp": now})
    # r.xadd("bar_stream:AMD", {"symbol": "AMD", "price": "5000", "timestamp": now})
        
    # threading.Event().wait()
        
    print("[Stream] Starting WebSocket stream...")
    asyncio.run(streamBars())

if __name__ == "__main__":
    main()