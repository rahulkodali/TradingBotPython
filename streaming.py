import asyncio
import websockets
import json
import os

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
URL = "wss://stream.data.alpaca.markets/v2/stocks"

async def stream_bars():
    async with websockets.connect(URL) as ws:
        await ws.send(json.dumps({
            "action": "auth",
            "key": API_KEY,
            "secret": SECRET_API_KEY
        }))
        print(await ws.recv()) 
