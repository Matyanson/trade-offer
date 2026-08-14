from time import sleep

from manager.main_manager import MainManager
from strategy.block_buy import BlockBuy
from setup.market_data import stock_client, crypto_client
from alpaca.data.requests import StockLatestQuoteRequest
from threading import Event
from datetime import datetime
print(datetime.now())

def get_current_ask_price(symbol):
    # Get current market price
    quote = crypto_client.get_crypto_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]

    return quote.ask_price

# 1) init manager
manager = MainManager()
manager.run()
sleep(2)  # Wait for streams to start

# 2) add a strategy to the manager
latest_price = get_current_ask_price("BTC/USD")
strategy = BlockBuy(manager, "BTC/USD", 0.001, latest_price, 50.0, 20.0)
manager.strategy.add("root", strategy)

# Keep application alive
try:
    Event().wait()
except KeyboardInterrupt:
    print("Shutting down...")