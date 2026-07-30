from manager.manager import StrategyManager
from setup.stream import crypto_stream
from alpaca.trading.enums import OrderSide
from strategy.block_buy import BlockBuy
from strategy.basic.trailing_stop_loss import TrailingStopLoss


# 1) init manager
manager = StrategyManager()

# 2) setup event listener for crypto quotes
crypto_stream.subscribe_quotes(
    manager.on_quote,
    "BTC/USD"
)

# 3) add a strategy to the manager
strategy = BlockBuy(manager, "BTC/USD", 0.001, 64_200.0, 100.0, 50.0)
manager.add("root", strategy)

crypto_stream.run()