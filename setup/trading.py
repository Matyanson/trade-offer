from setup.header import API_KEY, SECRET_KEY
from alpaca.trading.client import TradingClient


# paper=True means connect to the Paper Trading environment
trading_client = TradingClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    paper=True
)

# Request account information
account = trading_client.get_account()