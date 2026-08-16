from orders.model.order_interface import OrderInterface, OrderState
from alpaca.trading.enums import TimeInForce
from alpaca.trading.models import OrderType
from alpaca.trading.requests import LimitOrderRequest, OrderRequest, StopLimitOrderRequest, MarketOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestQuoteRequest
from setup.trading import trading_client
from setup.market_data import crypto_client
from alpaca.trading.models import Order

def get_order_type(entry_price: float, current_price: float) -> OrderType:
    
    # Price is already there -> buy immediately
    if abs(current_price - entry_price) < 0.01:
        return OrderType.MARKET
    # We want to buy lower -> limit order
    elif entry_price < current_price:
        return OrderType.LIMIT
    # We want to buy higher -> stop order
    else:
        return OrderType.STOP_LIMIT

def get_current_price(symbol: str) -> float:
    quote = crypto_client.get_crypto_latest_quote(
        StockLatestQuoteRequest(symbol_or_symbols=symbol)
    )[symbol]

    return float(quote.ask_price)

def buy_at_price_request(symbol: str, qty: int, time_in_force: TimeInForce, entry_price: float) -> OrderRequest:

    current_price = get_current_price(symbol)

    print(f"Current price: {current_price}")
    print(f"Target entry: {entry_price}")

    match get_order_type(entry_price, current_price):
        case OrderType.MARKET:
            order_data=MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=time_in_force,
            )
        case OrderType.LIMIT:
            order_data=LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                limit_price=entry_price,
                side=OrderSide.BUY,
                time_in_force=time_in_force,
            )
        case OrderType.STOP_LIMIT:
            order_data=StopLimitOrderRequest(
                symbol=symbol,
                qty=qty,
                stop_price=entry_price,
                limit_price=entry_price * 1.5,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.GTC,
            )

    return order_data


class EntryBuy(OrderInterface):
    """
    Represents a buy order for entering a position at a specific price.
    """

    def __init__(self, symbol: str, qty: float, target_price: float):
        self.target_price = target_price

        # place an entry
        order_data = buy_at_price_request(
            symbol=symbol,
            qty=qty,
            time_in_force=TimeInForce.GTC,
            entry_price=target_price
        )
        alpaca_order = trading_client.submit_order(order_data=order_data)
        
        super().__init__(symbol, qty, alpaca_order)
    

    def update(self):
        current_price = get_current_price(self.symbol)
        preferred_order_type = get_order_type(self.target_price, current_price)

        order_data = buy_at_price_request(
            symbol=self.symbol,
            qty=abs(self.budget.budget_qty),
            time_in_force=TimeInForce.GTC,
            entry_price=self.target_price
        )

        # CANCEL: the target price is not in the same direction as the current order type, we need to cancel the order request
        if self.alpaca_order.type != preferred_order_type:
            trading_client.cancel_order_by_id(self.alpaca_order.id)
            self.alpaca_order = trading_client.submit_order(order_data=order_data)
        # REPLACE
        else:
            self.alpaca_order = trading_client.replace_order_by_id(
                order_id=self.alpaca_order.id,
                order_data=order_data
            )
        return self.alpaca_order.id
