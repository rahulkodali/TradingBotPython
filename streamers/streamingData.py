import asyncio
import websockets
import json
import os
from backend.alpacaFunctions.updates.tradeExecutor import OrderType
from backend.models.stockHolding import Position

API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
URL = "wss://stream.data.alpaca.markets/v2/test" ##testing endpoint

class EMAEngine:
    def __init__(self, position_manager):
        self.position_manager = position_manager

    def updateEma(self, prev_ema, price, span):
        alpha = 2 / (span + 1)
        return (price * alpha) + (prev_ema * (1 - alpha))

    async def run(self):
        async with websockets.connect(URL) as ws:
            await ws.send(json.dumps({
                "action": "auth",
                "key": API_KEY,
                "secret": SECRET_API_KEY
            }))
            print(await ws.recv())  #connect response

            symbols = list(self.position_manager.positions.keys())

            await ws.send(json.dumps({
                "action": "subscribe",
                "bars": ["FAKEPACA"] ##change to symbols
            }))
            print(await ws.recv())  #auth confirmation

            ##testing
            while True:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    print("Live message:", data)
                except websockets.ConnectionClosed:
                    print("WebSocket closed")
                    break 

            # while True:
            #     msg = await ws.recv()
            #     data = json.loads(msg)[0]
            #     if data["T"] == "b":
            #         symbol = data["S"]
            #         price = data["c"]
            #         pos = self.position_manager.positions[symbol]
                    
            #         prev_ema21 = pos["ema21"]
            #         prev_ema50 = pos["ema50"]
            #         new_ema21 = self.update_ema(prev_ema21, price, 21)
            #         new_ema50 = self.update_ema(prev_ema50, price, 50)

            #         # Update stored EMAs
            #         pos["ema21"] = new_ema21
            #         pos["ema50"] = new_ema50

            #         # Check for cross
            #         if pos.status == Position.HOLDING and new_ema21 > new_ema50:
            #             print(f"Golden Cross for {symbol}")
            #             self.position_manager.executor.createOrder(symbol, pos.qty, OrderType.BUY)
            #             pos.status = Position.SOLD
            #         elif pos.status == Position.SOLD and new_ema21 < new_ema50:
            #             print(f"Death Cross for {symbol}")
            #             self.position_manager.executor.createOrder(symbol, pos.qty, OrderType.SELL)
            #             pos.status = Position.HOLDING


