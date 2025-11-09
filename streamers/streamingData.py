import asyncio
import websockets
import json
import os

from backend.alpacaFunctions.updates.tradeExecutor import OrderType
from backend.models.stockHolding import Position
from models import stockHolding
from managers.positionManager import PositionManager
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import defaultdict

symbolLocks = defaultdict(Lock)
threadExecutor = ThreadPoolExecutor(max_workers=20)
API_KEY = os.getenv("API_KEY")
SECRET_API_KEY = os.getenv("SECRET_API_KEY")
URL = "wss://stream.data.alpaca.markets/v2/test" ##testing endpoint

class EMAEngine:
    def __init__(self, positionManager: PositionManager):
        self.positionManager = positionManager
        self.symbolLocks = defaultdict(Lock)
        self.threadExecutor = ThreadPoolExecutor(max_workers=20)

    def updateEma(self, prev_ema, price, span):
        alpha = 2 / (span + 1)
        return (price * alpha) + (prev_ema * (1 - alpha))
    
    def handleBarUpdates(self, symbol: str, pos: stockHolding, price):
        with self.symbolLocks[symbol]:
            prevEma21 = pos["ema21"]
            prevEma50 = pos["ema50"]
            ema21 = self.updateEma(prevEma21, price, 21)
            ema50 = self.updateEma(prevEma50, price, 50)
            pos["ema21"] = ema21
            pos["ema50"] = ema50

            # Check for cross
            if pos.status == Position.SOLD and ema21 > ema50:
                print(f"Golden Cross for {symbol}")
                self.positionManager.executor.createOrder(symbol, pos.qty, OrderType.BUY)
                pos.status = Position.SOLD
            elif pos.status == Position.HOLDING and ema21 < ema50:
                print(f"Death Cross for {symbol}")
                self.positionManager.executor.createOrder(symbol, pos.qty, OrderType.SELL)
                pos.status = Position.HOLDING

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
            # while True:
            #     try:
            #         msg = await ws.recv()
            #         data = json.loads(msg)
            #         print("Live message:", data)
            #     except websockets.ConnectionClosed:
            #         print("WebSocket closed")
            #         break 

            while True:
                msg = await ws.recv()
                data = json.loads(msg)[0]
                if data["T"] == "b":
                    symbol = data["S"]
                    price = data["c"]
                    pos = self.positionManager.positions[symbol]

                    # Update stored EMAs
                    self.threadExecutor.submit(self.handleBarUpdates, symbol, pos, price)




