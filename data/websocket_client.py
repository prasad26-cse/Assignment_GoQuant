# import asyncio
# import threading
# import json
# import websockets
# import time

# latest_orderbook = None

# async def listen_orderbook():
#     global latest_orderbook
#     url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

#     while True:
#         try:
#             async with websockets.connect(
#                 url,
#                 ping_interval=20,   # send ping every 20 seconds
#                 ping_timeout=10     # wait 10 seconds for pong
#             ) as ws:
#                 print("Connected to WebSocket.")
#                 async for message in ws:
#                     try:
#                         data = json.loads(message)
#                         if all(k in data for k in ("timestamp", "exchange", "symbol", "asks", "bids")):
#                             latest_orderbook = data
#                         else:
#                             print("Unexpected message:", data)
#                     except Exception as e:
#                         print("Parsing error:", e)
#         except websockets.exceptions.ConnectionClosedError as e:
#             print(f"ConnectionClosedError: {e}. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)
#         except Exception as e:
#             print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
#             await asyncio.sleep(5)

# def start_websocket_listener():
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(listen_orderbook())

# def run_in_thread():
#     thread = threading.Thread(target=start_websocket_listener, daemon=True)
#     thread.start()
# def get_trade_metrics(orderbook, quantity, volatility, fee_tier):
#     """
#     Calculate trade metrics like slippage, fees, market impact, net cost,
#     maker/taker ratio, and internal latency based on orderbook and inputs.
#     This is a placeholder implementation - replace with your models.
#     """
#     import time
#     start_time = time.time()

#     # Dummy implementations - replace with your actual models:
#     slippage = 0.01 * quantity
#     fees = 0.001 * quantity  # e.g., 0.1%
#     market_impact = 0.005 * quantity
#     net_cost = slippage + fees + market_impact
#     maker_taker_ratio = 0.6  # dummy ratio
#     latency = (time.time() - start_time) * 1000  # in ms

#     return {
#         "slippage": slippage,
#         "fees": fees,
#         "market_impact": market_impact,
#         "net_cost": net_cost,
#         "maker_taker_ratio": maker_taker_ratio,
#         "latency": latency,
#     }
import asyncio
import threading
import json
import websockets
import time

latest_orderbook = None
_orderbook_lock = threading.Lock()

async def listen_orderbook():
    global latest_orderbook
    url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

    while True:
        try:
            async with websockets.connect(
                url,
                ping_interval=20,
                ping_timeout=10
            ) as ws:
                print("Connected to WebSocket.")
                async for message in ws:
                    try:
                        data = json.loads(message)
                        # Basic validation of message
                        if all(k in data for k in ("timestamp", "exchange", "symbol", "asks", "bids")):
                            with _orderbook_lock:
                                latest_orderbook = data
                        else:
                            print("Unexpected message format:", data)
                    except Exception as e:
                        print("Parsing error:", e)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"ConnectionClosedError: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def start_websocket_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_orderbook())

def run_in_thread():
    thread = threading.Thread(target=start_websocket_listener, daemon=True)
    thread.start()

def get_latest_orderbook():
    """Thread-safe access to latest orderbook."""
    with _orderbook_lock:
        return latest_orderbook

def get_trade_metrics(orderbook, quantity, volatility, fee_tier):
    """
    Calculate trade metrics like slippage, fees, market impact, net cost,
    maker/taker ratio, and internal latency based on orderbook and inputs.
    Replace with your actual models.
    """
    start_time = time.time()

    # Simple dummy calculations to replace with real logic:

    # Slippage modeled as a fraction of quantity scaled by volatility
    slippage = 0.01 * quantity * (1 + volatility / 10)

    # Fees tiered by fee_tier input (example dummy values)
    fee_tiers = {
        "Regular": 0.001,
        "VIP 1": 0.0007,
        "VIP 2": 0.0005
    }
    fee_rate = fee_tiers.get(fee_tier, 0.001)
    fees = fee_rate * quantity

    # Market impact dummy: proportional to sqrt(quantity)
    market_impact = 0.005 * (quantity ** 0.5)

    net_cost = slippage + fees + market_impact

    # Maker/taker ratio dummy values based on fee tier
    maker_taker_ratios = {
        "Regular": 0.6,
        "VIP 1": 0.7,
        "VIP 2": 0.8
    }
    maker_taker_ratio = maker_taker_ratios.get(fee_tier, 0.6)

    latency = (time.time() - start_time) * 1000  # in ms

    return {
        "slippage": slippage,
        "fees": fees,
        "market_impact": market_impact,
        "net_cost": net_cost,
        "maker_taker_ratio": maker_taker_ratio,
        "latency": latency,
    }
