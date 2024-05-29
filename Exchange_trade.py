import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import ccxt
from streamlit import secrets
import time
import pandas as pd
import math
import Trading_tools
from datetime import timedelta

class Exchange(object):

	def __init__(self, name='kucoin' ):
		self.adjust_timestamp_to_local_time = 2*60*60*1000	#currently +2hours UTC

		if name == 'kucoin':
			api_key = secrets['api_key_kucoin']
			api_secret = secrets['api_secret_kucoin']
			api_passphrase = secrets['api_passphrase_kucoin']
			
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
		elif name == 'binance':
			api_key = secrets['api_key_binance']
			api_secret = secrets['api_secret_binance']
			
			self.spot_exchange = ccxt.binance({
				'apiKey': api_key,
				'secret': api_secret,
			})
			#futures not available for binance

		
	def get_spot_fees(self):
		try:
			# Fetch trading fees from KuCoin
			trading_fees = self.exchange.fetch_trading_fees()
			return trading_fees
		except ccxt.BaseError as e:
			Trading_tools.append_to_file(f"An error occurred while fetching trading fees: {str(e)}")
			print(f"An error occurred while fetching trading fees: {str(e)}")
			return None

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

	def timeframe_to_int(self, interval=None):
		# If interval is provided, it must be at least 1 minute and df must be provided
		unit = interval[-1]
		if unit == 'm':
			interval = int(interval[:-1])
		elif unit == 'h':
			interval = int(interval[:-1]) * 60
		elif unit == 'd':
			interval = int(interval[:-1]) * 3600
		else:
			raise ValueError("Invalid interval format")

		if interval < 1:
			print("Error: Interval must be at least 1 minute.")
			return None

		return interval

	def calculate_time_diff_signal(self, interval=None, df=None, ticker_data=None):
		if df is None:
			print("Error: DataFrame must be provided when using an interval.")
			return None

		# Get the latest timestamp from the provided DataFrame
		last_timestamp = df['timestamp'].max()
		if ticker_data is None:
			current_timestamp = pd.Timestamp.now()
		else:
			current_timestamp = ticker_data['timestamp']
		# Calculate the time difference
		time_diff = current_timestamp - last_timestamp

		# If the time difference is greater than or equal to the interval, append the new data
		if time_diff >= timedelta(minutes=interval):
			#print(f"Time difference ({time_diff}) is equal than the interval ({interval} minutes) !!!!, last {last_timestamp}, current {current_timestamp} ")
			signal = True
		else:
			#print(f"Time difference ({time_diff}) is less than the interval ({interval} minutes). No data appended.")
			signal = False
		return signal

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

			if interval == None:
				df = new_df
			else:
				interval = self.timeframe_to_int(interval=interval)
				signal = self.calculate_time_diff_signal(interval=interval, df=df, ticker_data=ticker_data)
				# Get the latest timestamp from the provided DataFrame
				if signal:		
					df = pd.concat([df, new_df], ignore_index=True)
					#print(f"Data appended to DataFrame for symbol: {symbol}")


			return df

		except ccxt.BaseError as e:
			print("An error occurred while fetching the ticker:", str(e))
			return df

	def fetch_klines(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=200, market_type='spot'):
		"""Fetch klines (candlestick data) for a specific symbol and return a DataFrame."""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
			df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
			df['timestamp'] = pd.to_datetime(df['timestamp']+self.adjust_timestamp_to_local_time, unit='ms')
			interval = self.timeframe_to_int(interval=timeframe) * 2 #needed cause it happens that it take it little more than interval to update klines
			signal = self.calculate_time_diff_signal(interval=interval, df=df, ticker_data=None)
			if signal:
				raise ValueError(f"not able to fetch all klines, timestamp gap last {df['timestamp'].max()}, current {pd.Timestamp.now()}")
			return df
		except ccxt.BaseError as e:
			print("An error occurred while fetching klines:", str(e))
			return None

	def fetch_market_data(self, symbol, market_type='spot'):
		"""Fetch market data for the given symbol."""
		exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
		return exchange.market(symbol)

	def place_market_order(self, symbol='BTC/USDT', percentage=100, order_type='buy', market_type='spot', leverage=None, reduceOnly=False):
		#percentage shall be 1 to close futures position
		
		if market_type == 'spot':
			base_currency, quote_currency = symbol.split('/')
		else:
			base_currency, quote_currency = symbol[:-5], 'USDT'  # Futures symbols end with 'M' (e.g., ETHUSDTM)
        
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			# Fetch the available balance for the right currency
			balance_currency = base_currency if order_type == 'sell' and market_type == 'spot' else quote_currency
			balance_type = 'total' if market_type == 'futures' else 'free'
			available_balance = self.fetch_balance(balance_currency, balance_type, market_type)

			if available_balance is None:
				print("Could not fetch the available balance.")
				return

			# Fetch market data to get the precision and limits
			market_data = self.fetch_market_data(symbol, market_type)
			precision = market_data['precision']['amount']
			min_order_amount = market_data['limits']['amount']['min']
			multiplier = market_data['contractSize']	#multiplier in API, https://stackoverflow.com/questions/75522901/issue-with-kucoin-futures-api-to-create-limit-order 

			# Determine the number of decimal places from the precision value
			precision_decimal_places = max(0, int(-math.log10(precision)))

			params = {'reduceOnly':reduceOnly}

			price = None
            		
			if order_type == 'buy':
				# Fetch the ticker price to calculate max quantity
				ticker = exchange.fetch_ticker(symbol)
				price = ticker['last']
                
				# Calculate quantity based on the percentage of available balance
				quantity = (available_balance * (percentage / 100)) / (price * multiplier)

			elif order_type == 'sell':
				# Calculate quantity based on the percentage of available balance
				quantity = float(available_balance * (percentage / 100) / multiplier)	

			else:
				raise ValueError("order_type must be 'buy' or 'sell'")

			print("params:", params)

			# Ensure the quantity is within the allowed precision and limits
			quantity = max(min_order_amount, round(quantity, precision_decimal_places))

			# Set leverage if provided and if market type is futures
			if leverage is not None and market_type == 'futures':
				params['leverage'] = leverage

			Trading_tools.append_to_file(f"{symbol} precision is {precision} and min_order_amount is {min_order_amount}") 
			Trading_tools.append_to_file(f"order is {order_type}, price is {price} and quantity is {quantity}")
			Trading_tools.append_to_file(f"Available balance for {balance_currency}: {available_balance}")
			print(f"{symbol} precision is {precision} and min_order_amount is {min_order_amount}") 
			print(f"order is {order_type}, price is {price} and quantity is {quantity}, leverage is {leverage}")
			print(f"Available balance for {balance_currency}: {available_balance}")

			# Place a market buy order
			order = exchange.create_order(symbol=symbol, type='market', side=order_type, amount=quantity, params=params)
			Trading_tools.append_to_file(f"Order placed: {order}")
			print("Order placed:", order)
			return order
		except ccxt.BaseError as e:
			Trading_tools.append_to_file(f"An error occurred while placing the order: {str(e)}")
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






