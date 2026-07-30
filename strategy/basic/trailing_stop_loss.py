from strategy.model.strategy import Strategy, StrategyState
from alpaca.trading.enums import OrderSide, OrderStatus, TimeInForce
from alpaca.trading.requests import StopLimitOrderRequest
from alpaca.data.models import Quote
from setup.trading import trading_client

class TrailingStopLoss(Strategy):
    def __init__(self, manager, symbol: str, qty: float, trail_distance: float, order_side: OrderSide):
        self.trail_distance = trail_distance
        self.trailing_stop_order = None
        self.order_side = order_side

        super().__init__(manager, symbol, qty)

    def get_stop_limit_price(self, quote: Quote):
        if self.order_side == OrderSide.SELL:
            stop_price = quote.bid_price - self.trail_distance
            limit_price = stop_price * 0.5
        else:
            stop_price = quote.ask_price + self.trail_distance
            limit_price = stop_price * 1.5
        return stop_price, limit_price

    def place_entry_order(self, quote: Quote):
        # Place a market order to buy the asset
        stop_price, limit_price = self.get_stop_limit_price(quote)
        self.trailing_stop_order = trading_client.submit_order(
            order_data=StopLimitOrderRequest(
                symbol=self.symbol,
                qty=self.qty,
                stop_price=stop_price,
                limit_price=limit_price,
                side=self.order_side,
                time_in_force=TimeInForce.GTC
            )
        )
        print(f"{self.name}: Placed entry order for {self.symbol} at stop price: {stop_price}, limit price: {limit_price}")

    def move_trailing_stop(self, quote: Quote):
        if self.trailing_stop_order is None:
            return  # No trailing stop order to move

        stop_price, limit_price = self.get_stop_limit_price(quote)
        self.trailing_stop_order = trading_client.get_order_by_id(self.trailing_stop_order.id)
        previous_stop_price = float(self.trailing_stop_order.stop_price)

        if self.order_side == OrderSide.SELL and stop_price > previous_stop_price:
            # Move the trailing stop up for a sell order
            self.trailing_stop_order = trading_client.replace_order_by_id(
                order_id=self.trailing_stop_order.id,
                order_data=StopLimitOrderRequest(
                    symbol=self.symbol,
                    qty=self.qty,
                    stop_price=stop_price,
                    limit_price=limit_price,
                    side=self.order_side,
                    time_in_force=TimeInForce.GTC
                )
            )
            print(f"{self.name}: Moved trailing stop up for {self.symbol} to stop price: {stop_price}, limit price: {limit_price}")
        elif self.order_side == OrderSide.BUY and stop_price < previous_stop_price:
            # Move the trailing stop down for a buy order
            self.trailing_stop_order = trading_client.replace_order_by_id(
                order_id=self.trailing_stop_order.id,
                order_data=StopLimitOrderRequest(
                    symbol=self.symbol,
                    qty=self.qty,
                    stop_price=stop_price,
                    limit_price=limit_price,
                    side=self.order_side,
                    time_in_force=TimeInForce.GTC
                )
            )
            print(f"{self.name}: Moved trailing stop down for {self.symbol} to stop price: {stop_price}, limit price: {limit_price}")
    
    def is_stop_loss_filled(self):
        if self.trailing_stop_order is None:
            return False
        
        self.trailing_stop_order = trading_client.get_order_by_id(self.trailing_stop_order.id)
        return self.trailing_stop_order.status == OrderStatus.FILLED
    
    def on_init(self):
        return super().on_init()

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
        