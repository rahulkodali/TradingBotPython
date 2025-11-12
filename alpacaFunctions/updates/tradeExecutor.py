
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
    if response.status_code != 200:
        print(f"[Order Failed] {response.status_code} - {response.text}")
        response.raise_for_status()

    data = response.json()
    print(f"[Order Placed] {data['side'].upper()} {data['qty']} {data['symbol']} | Status: {data['status']} | ID: {data['id']}")
    return data

