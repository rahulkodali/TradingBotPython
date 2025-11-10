
import requests
from enum import Enum
from managers.initializer import HEADERS

URL = "https://paper-api.alpaca.markets/v2/orders"

class OrderType(Enum):
    SELL = "sell"
    BUY = "buy"

def createOrder(symbol: str, qty: int, orderType: OrderType):
    
    params = {
        "type":"market",
        "time_in_force":"day",
        "symbol":symbol,
        "qty":qty,
        "side": orderType.value
    }

    response = requests.post(URL, headers=HEADERS, json=params)
    print(response.text)
    response.raise_for_status()
    data = response.json()
    print(data)
    return data

