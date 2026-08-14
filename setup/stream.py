from setup.header import API_KEY, SECRET_KEY
from alpaca.data.live.stock import StockDataStream
from alpaca.data.live.crypto import CryptoDataStream
from alpaca.trading.stream import TradingStream

stock_stream = StockDataStream(API_KEY, SECRET_KEY)
crypto_stream = CryptoDataStream(API_KEY, SECRET_KEY)
trading_stream = TradingStream(API_KEY, SECRET_KEY)