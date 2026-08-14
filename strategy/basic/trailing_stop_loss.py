from manager.main_manager import MainManager
from orders.model.order_interface import OrderState
from orders.stop_order import StopOrder
from strategy.model.strategy import Strategy, StrategyState
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.trading.requests import StopLimitOrderRequest
from alpaca.data.models import Quote
from setup.trading import trading_client

class TrailingStopLoss(Strategy):
    def __init__(self, manager: MainManager, symbol: str, qty: float, trail_distance: float, order_side: OrderSide):
        self.trail_distance: float = trail_distance
        self.trailing_stop_order: StopOrder = None
        self.order_side: OrderSide = order_side

        super().__init__(manager, symbol, qty)

    def get_stop_price(self, quote: Quote):
        if self.order_side == OrderSide.SELL:
            stop_price = quote.bid_price - self.trail_distance
        else:
            stop_price = quote.ask_price + self.trail_distance
        return stop_price

    def place_entry_order(self, quote: Quote):
        # Place a market order to buy the asset
        stop_price = self.get_stop_price(quote)
        self.trailing_stop_order = StopOrder(
            symbol=self.symbol,
            qty=self.budget_qty,
            stop_price=stop_price,
            side=self.order_side
        )
        self.manager.order.add(self.id, self.trailing_stop_order)
        print(f"{self.name}: Placed entry order for {self.symbol} at stop price: {stop_price}, quantity: {self.budget_qty}")

    def move_trailing_stop(self, quote: Quote):
        if self.trailing_stop_order is None:
            return  # No trailing stop order to move

        stop_price = self.get_stop_price(quote)
        previous_stop_price = self.trailing_stop_order.stop_price

        if (self.order_side == OrderSide.SELL and stop_price > previous_stop_price or
            self.order_side == OrderSide.BUY and stop_price < previous_stop_price):
            # Move the trailing stop up/down for a sell order
            self.trailing_stop_order.stop_price = stop_price
            self.manager.order.update(str(self.trailing_stop_order.alpaca_order.id))

            print(f"{self.name}: Moved trailing stop up/down for {self.symbol} to stop price: {stop_price}")
    
    def is_stop_loss_filled(self):
        if self.trailing_stop_order is None:
            return False
        
        return self.trailing_stop_order.state == OrderState.ACTIVE
    
    def on_init(self):
        return super().on_init()

    def update_budget(self):
        # Update the budget distribution for the strategy and its orders
        self.filled_qty = 0.0
        self.position_qty = 0.0
        self.reserved_qty = 0.0

        if self.trailing_stop_order is not None:
            self.available_qty = self.trailing_stop_order.available_qty
            self.reserved_qty = self.trailing_stop_order.reserved_qty
            self.position_qty = self.trailing_stop_order.position_qty
            self.filled_qty = self.trailing_stop_order.filled_qty
        
        self.available_qty = self.budget_qty - self.filled_qty - self.reserved_qty

    async def on_quote(self, quote):
        if self.state == StrategyState.FINISHED:
            return  # No further action needed

        # 0) Place the entry order
        if self.trailing_stop_order is None:
            self.place_entry_order(quote)
            return
        
        elif self.is_stop_loss_filled():
            self.state = StrategyState.FINISHED
            print(f"{self.name}: Trailing stop loss filled for {self.symbol}. Strategy is now FINISHED.")
            return

        else:
            # 1) manually modify the stop loss order if the price has moved up
            self.move_trailing_stop(quote)
        