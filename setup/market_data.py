from setup.header import API_KEY, SECRET_KEY

from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient

# No keys required for stock data
stock_client = StockHistoricalDataClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY
)

crypto_client = CryptoHistoricalDataClient()