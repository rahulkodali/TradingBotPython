import websockets, json, os, redis

from datetime import timezone, datetime


API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
URL = "wss://stream.data.alpaca.markets/v2/test" ##testing endpoint
UTC = timezone.utc
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

async def streamBars():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({
            "action": "auth",
            "key": API_KEY,
            "secret": SECRET_API_KEY
        }))
        print(await ws.recv())  #connect response

        symbols = [key.split(":")[1] for key in r.keys("position:*")]

        await ws.send(json.dumps({
            "action": "subscribe",
            "bars": ["FAKEPACA"] ##change to symbols
        }))
        print(await ws.recv())  #auth confirmation

        ##testing
        # while True:
        #     try:
        #         msg = await ws.recv()
        #         data = json.loads(msg)
        #         print("Live message:", data)
        #     except websockets.ConnectionClosed:
        #         print("WebSocket closed")
        #         break 

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)[0]
                if data["T"] == "b":
                    bar = {
                        "symbol": data["S"],
                        "price": float(data["c"]),
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                    r.xadd(f"bar_stream:{bar['symbol']}", bar)
                    print(f"Published: {bar}")
            except Exception as e:
                print(f"[ERROR] WebSocket processing error: {e}")
                continue




