import ccxt
from streamlit import secrets
import time
import pandas as pd
import math

class Kucoin(object):

	def __init__(self):
		api_key = secrets['api_key']
		api_secret = secrets['api_secret']
		api_passphrase = secrets['api_passphrase']
		
		self.spot_exchange = ccxt.kucoin({
			'apiKey': api_key,
			'secret': api_secret,
			'password': api_passphrase,  # KuCoin requires a password (passphrase)
		})
		self.futures_exchange = ccxt.kucoinfutures({
			'apiKey': api_key,
			'secret': api_secret,
			'password': api_passphrase,  # KuCoin Futures requires a password (passphrase)
		})
		self.adjust_timestamp_to_local_time = 2*60*60*1000	#currently +2hours UTC

	def fetch_balance(self, currency='USDT', account='free', market_type='spot'):
		# fetching the current balance
		# can be free, used, total
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			balance_all = exchange.fetch_balance()
			balance = balance_all[account].get(currency, None)

			print("Balance:", balance, currency)
			return balance
		except ccxt.BaseError as e:
			print("An error occurred:", str(e))

	def fetch_ticker(self, symbol='BTC/USDT', df=None, interval=None, market_type='spot'):
		"""Fetch ticker information for a specific symbol and append it to the provided DataFrame."""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			# Fetch current ticker data
			ticker = exchange.fetch_ticker(symbol)
			ticker_data = {
				'timestamp': pd.to_datetime(ticker['timestamp']+self.adjust_timestamp_to_local_time, unit='ms'),
				'open': ticker['open'],
				'high': ticker['high'],
				'low': ticker['low'],
				'close': ticker['close'],
				'last': ticker['last'],
				'volume': ticker['baseVolume']
			}
			new_df = pd.DataFrame([ticker_data])

			# If interval is None, return the current price (append to df if provided)
			if interval is None:
				if df is not None:
					df = pd.concat([df, new_df], ignore_index=True)
				return df if df is not None else new_df

			# If interval is provided, it must be at least 1 minute and df must be provided
			if interval < 1:
				print("Error: Interval must be at least 1 minute.")
				return None

			if df is None:
				print("Error: DataFrame must be provided when using an interval.")
				return None

			# Get the latest timestamp from the provided DataFrame
			if not df.empty:
				last_timestamp = df['timestamp'].max()
				current_timestamp = ticker_data['timestamp']

				# Calculate the time difference
				time_diff = current_timestamp - last_timestamp

				# If the time difference is greater than or equal to the interval, append the new data
				if time_diff >= timedelta(minutes=interval):
					df = pd.concat([df, new_df], ignore_index=True)
					print(f"Data appended to DataFrame for symbol: {symbol}")
				else:
					print(f"Time difference ({time_diff}) is less than the interval ({interval} minutes). No data appended.")
			else:
				df = new_df

			return df

		except ccxt.BaseError as e:
			print("An error occurred while fetching the ticker:", str(e))
			return df

	def fetch_klines(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=100, market_type='spot'):
		"""Fetch klines (candlestick data) for a specific symbol and return a DataFrame."""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
			df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
			df['timestamp'] = pd.to_datetime(df['timestamp']+self.adjust_timestamp_to_local_time, unit='ms')
			return df
		except ccxt.BaseError as e:
			print("An error occurred while fetching klines:", str(e))
			return None

	def fetch_market_data(self, symbol, market_type='spot'):
		"""Fetch market data for the given symbol."""
		exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
		return exchange.market(symbol)

	def place_market_order(self, symbol='BTC/USDT', percentage=100, order_type='buy', market_type='spot', leverage=None):
		#percentage shall be 1 to close futures position
		
		if market_type == 'spot':
			base_currency, quote_currency = symbol.split('/')
		else:
			base_currency, quote_currency = symbol[:-5], 'USDT'  # Futures symbols end with 'M' (e.g., ETHUSDTM)
        
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			# Fetch the available balance for the right currency
			available_balance = self.fetch_balance(base_currency if order_type == 'sell' and market_type == 'spot' else quote_currency, \
				'used' if order_type == 'sell' and market_type == 'futures' else 'free', market_type)

			if available_balance is None:
				print("Could not fetch the available balance.")
				return

			# Fetch market data to get the precision and limits
			market_data = self.fetch_market_data(symbol, market_type)
			precision = market_data['precision']['amount']
			min_order_amount = market_data['limits']['amount']['min']
			print(f"{symbol} precision is {precision} and min_order_amount is {min_order_amount}")

			# Determine the number of decimal places from the precision value
			precision_decimal_places = abs(int(math.log10(precision)))

			params = {}
            
			if order_type == 'buy':
				# Fetch the ticker price to calculate max quantity
				ticker = exchange.fetch_ticker(symbol)
				price = ticker['last']
                
				# Calculate quantity based on the percentage of available balance
				quantity = (available_balance * (percentage / 100)) / price

			elif order_type == 'sell':
				# Calculate quantity based on the percentage of available balance
				quantity = float(available_balance * (percentage / 100))	

				# Place a market sell order
				if market_type == 'futures' and order_type == 'sell':
					params['reduceOnly'] = True
			else:
				raise ValueError("order_type must be 'buy' or 'sell'")

			print("params:", params)

			# Ensure the quantity is within the allowed precision and limits
			quantity = max(min_order_amount, round(quantity, precision_decimal_places))

			# Set leverage if provided and if market type is futures
			if leverage is not None and market_type == 'futures':
				params['leverage'] = leverage

			# Place a market buy order
			order = exchange.create_order(symbol=symbol, type='market', side=order_type, amount=quantity, params=params)

			print("Order placed:", order)
		except ccxt.BaseError as e:
			print("An error occurred while placing the order:", str(e))

	def get_open_orders(self, market_type='spot'):
		# Check open orders
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			open_orders = self.exchange.fetch_open_orders('BTC/USDT')
			print("Open orders:", open_orders)
			return open_orders
		except ccxt.BaseError as e:
			print("An error occurred while fetching open orders:", str(e))


if __name__ == "__main__":
	kucoin = Kucoin()
	#kucoin.fetch_balance(currency='USDT', account='free', market_type='futures')
	#kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
	#kucoin.fetch_ticker(symbol='XBTUSDTM', market_type='futures')
	#kucoin.fetch_klines(symbol='XBTUSDTM', limit=200, market_type='futures')
	#kucoin.place_market_order(symbol='ETH/USDT', percentage=50, order_type='buy', market_type='spot')
	#kucoin.place_market_order(symbol='ETHUSDTM', percentage=25, order_type='buy', market_type='futures', leverage=None)
