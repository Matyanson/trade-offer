from turtle import position

from manager.main_manager import MainManager
from manager.strategy_manager.manager import StrategyManager
from orders.entry_buy import EntryBuy
from orders.model.order_interface import OrderInterface, OrderState
from orders.stop_order import StopOrder
from strategy.basic.trailing_stop_loss import TrailingStopLoss
from strategy.model.strategy import Strategy, StrategyState
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.trading.requests import StopLimitOrderRequest, StopOrderRequest, TrailingStopOrderRequest
from alpaca.trading.models import Order
from alpaca.data.models import Quote

from strategy.utils.entry import buy_at_price

class BlockBuy(Strategy):
    def __init__(self, manager: MainManager, symbol: str, qty: float, entry_price: float, stop_loss_distance: float, trail_start_distance: float):
        self.entry_price: float = entry_price
        self.stop_loss_distance: float = stop_loss_distance
        self.trail_start_distance: float = trail_start_distance
        self.filled_entry_price: float | None = None
        
        # Child strategies & orders
        self.entry_order: OrderInterface | None = None
        self.stop_loss_order: OrderInterface | None = None
        self.trailing_stop_order: Strategy | None = None
        
        super().__init__(manager, symbol, qty)

    

    def check_entry_fill(self):
        if self.entry_order.state != OrderState.FINISHED:
            return  # Wait for the order to be fully filled
        
        self.state = StrategyState.ACTIVE
        print(f"BlockBuy strategy {self.id} is now ACTIVE.")
        print(f"BlockBuy strategy {self.id} entry filled at price: {self.entry_order.alpaca_order.filled_avg_price}.")
        self.filled_entry_price = float(self.entry_order.alpaca_order.filled_avg_price)

        # 3) set a stop loss
        entry_qty = self.entry_order.budget.position_qty

        self.stop_loss_order = StopOrder(
            symbol=self.symbol,
            qty=entry_qty,
            stop_price=self.filled_entry_price - self.stop_loss_distance,
            side=OrderSide.SELL
        )
        self.manager.order.add(self.id, self.stop_loss_order)
        print(f"BlockBuy strategy {self.id} stop loss order placed: {self.stop_loss_order.id} at stop price: {self.filled_entry_price - self.stop_loss_distance}. quantity: {entry_qty}.")
    
    def cancel_stop_loss(self):
        if self.stop_loss_order is not None:
            try:
                self.stop_loss_order.cancel()
                self.stop_loss_order = None
                print(f"BlockBuy strategy {self.id} stop loss order {self.stop_loss_order.id} canceled.")
            except Exception as e:
                print(f"Error occurred while canceling stop loss order: {e}")

    def check_trailing_activation(self, quote: Quote):
        price = quote.bid_price
        trail_start_price = self.filled_entry_price + self.trail_start_distance

        if price >= trail_start_price:
            self.cancel_stop_loss()

            qty = self.entry_order.budget.position_qty
            self.trailing_stop_order = TrailingStopLoss(
                manager=self.manager,
                symbol=self.symbol,
                qty=qty,
                trail_distance=self.trail_start_distance,
                order_side=OrderSide.SELL
            )
            self.manager.strategy.add(self.id, self.trailing_stop_order)
            print(f"BlockBuy strategy {self.id} has activated trailing stop. At price: {price}, trail start price: {trail_start_price}. Trailing stop strategy id: {self.trailing_stop_order.id}.")

    def is_stop_loss_filled(self):
        if self.stop_loss_order is None:
            return False
        
        return self.stop_loss_order.state == OrderState.FINISHED

    def on_init(self):
        print("BlockBuy oninit called.")
        # 1) Place a buy order at a specific price

        self.entry_order = EntryBuy(
            symbol=self.symbol,
            qty=self.budget.budget_qty,
            target_price=self.entry_price
        )
        self.manager.order.add(self.id, self.entry_order)
        print(f"BlockBuy strategy {self.id} placed entry order: {self.entry_order.id}.")

    async def on_quote(self, quote):
        match self.state:
            case StrategyState.FINISHED:
                    return  # No further action needed

            # 2) Wait for the order to be filled
            case StrategyState.PENDING:
                self.check_entry_fill()
        
            case StrategyState.ACTIVE:
                # 3) Check if the stop loss order has been filled
                if self.is_stop_loss_filled():
                    self.state = StrategyState.FINISHED
                    print(f"BlockBuy strategy {self.id} stop loss filled. Strategy is now FINISHED.")
                    return
                
                # 4) set a trailing stop loss
                if self.filled_entry_price != None and self.trailing_stop_order == None:
                    self.check_trailing_activation(quote)
                
                # 5) Check if the trailing stop loss strategy has finished
                if self.trailing_stop_order is not None and self.trailing_stop_order.state == StrategyState.FINISHED:
                    self.state = StrategyState.FINISHED
                    print(f"BlockBuy strategy {self.id} trailing stop loss finished. Strategy is now FINISHED.")
