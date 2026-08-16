from orders.model.order_interface import OrderInterface, OrderState
from alpaca.trading.enums import OrderSide, TimeInForce
from setup.trading import trading_client
from alpaca.trading.requests import StopLimitOrderRequest


class StopLimit(OrderInterface):
    """
    Represents a stop-limit order at a specific price.
    """

    def __init__(self, symbol: str, qty: float, stop_price: float, limit_price: float, side: OrderSide):
        self.stop_price = stop_price
        self.limit_price = limit_price
        self.side = side

        # place an entry
        self.stop_loss_order = trading_client.submit_order(
            order_data=StopLimitOrderRequest(
                symbol=self.symbol,
                qty=qty,
                stop_price=self.stop_price,
                limit_price=self.limit_price,
                side=self.side,
                time_in_force=TimeInForce.GTC
            )
        )
        super().__init__(symbol, qty, self.stop_loss_order)

    def update(self):
        """
        Replace the order with a new one (updating the stop price, limit price, etc.)
        """ 

        # place a new order with updated parameters
        self.stop_loss_order = trading_client.replace_order_by_id(
            order_id=self.stop_loss_order.id,
            order_data=StopLimitOrderRequest(
                symbol=self.symbol,
                qty=abs(self.budget.budget_qty),
                stop_price=self.stop_price,
                limit_price=self.limit_price,
                side=self.side,
                time_in_force=TimeInForce.GTC
            )
        )

        return self.stop_loss_order.id