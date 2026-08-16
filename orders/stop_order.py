from orders.model.order_interface import OrderInterface, OrderState
from alpaca.trading.enums import OrderSide, TimeInForce
from setup.trading import trading_client
from alpaca.trading.requests import StopLimitOrderRequest


class StopOrder(OrderInterface):
    """
    Represents a stop order at a specific price.
    """

    def _get_limit_price(self, order_side: OrderSide):
        if order_side == OrderSide.SELL:
            return self.stop_price * 0.5
        else:
            return self.stop_price * 1.5

    def __init__(self, symbol: str, qty: float, stop_price: float, side: OrderSide):
        self.stop_price = stop_price
        self.side = side
        self.limit_price = self._get_limit_price(side)

        # place an entry
        self.alpaca_order = trading_client.submit_order(
            order_data=StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                stop_price=self.stop_price,
                limit_price=self.limit_price,
                side=self.side,
                time_in_force=TimeInForce.GTC
            )
        )
        super().__init__(symbol, qty, self.alpaca_order)

    def update(self):
        """
        Replace the order with a new one (updating the stop price, limit price, etc.)
        """ 

        # place a new order with updated parameters
        self.limit_price = self._get_limit_price(self.side)
        self.alpaca_order = trading_client.replace_order_by_id(
            order_id=self.alpaca_order.id,
            order_data=StopLimitOrderRequest(
                symbol=self.symbol,
                qty=abs(self.budget.budget_qty),
                stop_price=self.stop_price,
                limit_price=self.limit_price,
                side=self.side,
                time_in_force=TimeInForce.GTC
            )
        )

        return self.alpaca_order.id