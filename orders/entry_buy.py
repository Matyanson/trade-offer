from orders.model.order_interface import OrderInterface, OrderState
from alpaca.trading.enums import TimeInForce
from alpaca.trading.models import OrderType
from alpaca.trading.requests import LimitOrderRequest, StopLimitOrderRequest, MarketOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestQuoteRequest
from setup.trading import trading_client
from setup.market_data import crypto_client
from alpaca.trading.models import Order

def buy_at_price(symbol: str, qty: int, time_in_force: TimeInForce, entry_price: float) -> Order:
    # Get current market price
    quote = crypto_client.get_crypto_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]

    current_price = quote.ask_price

    print(f"Current price: {current_price}")
    print(f"Target entry: {entry_price}")

    # Price is already there -> buy immediately
    if abs(current_price - entry_price) < 0.01:
        order = trading_client.submit_order(
            order_data=MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=time_in_force,
            )
        )

    # We want to buy lower -> limit order
    elif entry_price < current_price:
        order = trading_client.submit_order(
            order_data=LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                limit_price=entry_price,
                side=OrderSide.BUY,
                time_in_force=time_in_force,
            )
        )

    # We want to buy higher -> stop order
    else:
        order = trading_client.submit_order(
            order_data=StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                stop_price=entry_price,
                limit_price=entry_price * 1.5,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
            )
        )

    return order


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
            match self.alpaca_order.type:
                case OrderType.LIMIT:
                    order_class = LimitOrderRequest
                case OrderType.STOP_LIMIT:
                    order_class = StopLimitOrderRequest
                case OrderType.MARKET:
                    order_class = MarketOrderRequest
                case _:
                    raise ValueError(f"Unsupported order type: {self.alpaca_order.type}")

            # place a new order with updated parameters
            self.alpaca_order = trading_client.replace_order_by_id(
                order_id=self.alpaca_order.id,
                order_data=order_class(
                    symbol=self.symbol,
                    qty=abs(self.budget.budget_qty),
                    stop_price=self.stop_price,
                    limit_price=self.limit_price,
                    side=self.side,
                    time_in_force=TimeInForce.GTC
                )
            )

            return self.alpaca_order.id