from orders.model.order_interface import OrderInterface, OrderState
from alpaca.trading.enums import TimeInForce
from strategy.utils.entry import buy_at_price


class EntryBuy(OrderInterface):
    """
    Represents a buy order for entering a position at a specific price.
    """

    def __init__(self, symbol: str, qty: float, target_price: float):
        self.target_price = target_price

        # place an entry
        alpaca_order = buy_at_price(
            symbol=symbol,
            qty=qty,
            time_in_force=TimeInForce.GTC,
            entry_price=target_price
        )
        
        super().__init__(symbol, qty, alpaca_order)

    def update(self):
            """
            Replace the order with a new one (updating the stop price, limit price, etc.)
            """

            # place a new order with updated parameters
            self.alpaca_order = buy_at_price(
                symbol=self.symbol,
                qty=self.budget.budget_qty,
                time_in_force=TimeInForce.GTC,
                entry_price=self.target_price
            )
        
            return self.alpaca_order.id