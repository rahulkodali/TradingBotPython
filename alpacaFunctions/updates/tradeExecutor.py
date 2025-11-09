
import requests
from enum import Enum

URL = "https://paper-api.alpaca.markets/v2/orders"

class OrderType(Enum):
    SELL = "sell"
    BUY = "buy"

class TradeExecutor:
    def __init__(self, headers):
        self.headers = headers

    def createOrder(self, symbol: str, qty: int, orderType: OrderType):
        params = {
            "type":"market",
            "time_in_force":"day",
            "symbol":symbol,
            "qty":qty,
            "side": orderType.value
        }

        response = requests.post(URL, headers=self.headers, json=params)
        print(response.text)
        response.raise_for_status()
        data = response.json()
        print(data)
        return data

