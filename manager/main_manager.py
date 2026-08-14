from threading import Thread

from manager.main_manager_interface import MainManagerInterface
from manager.strategy_manager.manager import StrategyManager
from manager.order_manager.manager import OrderManager
from manager.budget_manager import BudgetManager
from setup.stream import crypto_stream
from setup.stream import trading_stream


class MainManager(MainManagerInterface):

    def __init__(self):
        # 1) init managers
        self.strategy = StrategyManager()
        self.order = OrderManager(self)
        self.budget = BudgetManager(self)

        # 2) setup event listeners
        crypto_stream.subscribe_quotes(
            self.strategy.on_quote,
            "BTC/USD"
        )

        trading_stream.subscribe_trade_updates(
            self.order.on_trade_update
        )

    def run(self):
        # 3) activate streams in different threads
        crypto_thread = Thread(
            target=crypto_stream.run,
            daemon=True,
        )

        trading_thread = Thread(
            target=trading_stream.run,
            daemon=True,
        )

        trading_thread.start()
        print("Trading stream started.")
        crypto_thread.start()
        print("Crypto stream started.")