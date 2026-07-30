from alpaca.trading.requests import LimitOrderRequest, StopLimitOrderRequest, MarketOrderRequest, StopOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.requests import StockLatestQuoteRequest
from setup.trading import trading_client
from setup.market_data import stock_client, crypto_client
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