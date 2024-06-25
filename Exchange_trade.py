import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import ccxt
from streamlit import secrets
import time
import pandas as pd
import math
import Sharing_data
from datetime import timedelta
import asyncio

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

	def load_market(self, market_type='spot'):
		# solve some connection bug
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			exchange.load_markets()
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred: {str(e)}")
		
	def get_spot_fees(self):
		try:
			# Fetch trading fees from KuCoin
			trading_fees = self.exchange.fetch_trading_fees()
			return trading_fees
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching trading fees: {str(e)}")
			return None

	def fetch_balance(self, currency='USDT', account='free', market_type='spot'):
		# fetching the current balance
		# can be free, used, total
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			balance_all = exchange.fetch_balance()
			balance = balance_all[account].get(currency, None)

			Sharing_data.append_to_file(f"Balance: {balance} {currency}")
			return balance
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred: {str(e)}")

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
			Sharing_data.append_to_file("Error: Interval must be at least 1 minute.")
			return None

		return interval

	def calculate_time_diff_signal(self, interval=None, df=None, ticker_data=None):
		if df is None:
			Sharing_data.append_to_file("Error: DataFrame must be provided when using an interval.")
			return None

		# Get the latest timestamp from the provided DataFrame
		last_timestamp = df['timestamp'].iloc[-1]
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

	def fetch_klines(self, symbol='BTC/USDT', timeframe='1m', since=None, limit=200, market_type='spot'):
		"""Fetch klines (candlestick data) for a specific symbol and return a DataFrame."""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
			df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
			df['timestamp'] = pd.to_datetime(df['timestamp']+self.adjust_timestamp_to_local_time, unit='ms')
			return df
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching klines: {str(e)}")
			return None
		except Exception as e:
			Sharing_data.append_to_file(f"An error occurred after fetching klines: {str(e)}")


	def fetch_ticker(self, symbol='BTC/USDT', df=None, interval=None, market_type='spot'):
		"""Fetch ticker information for a specific symbol and append it to the provided DataFrame."""
		try:
			updated = False
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			new_df = self.fetch_klines(symbol=symbol, timeframe=interval, since=None, limit=1, market_type=market_type)
			"""
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
			"""
			if new_df is None:
				Sharing_data.append_to_file(f"An error occurred while fetching ticker, df is None")
			elif interval == None:
				df = new_df
				updated = True
			else:
				interval = self.timeframe_to_int(interval=interval)
				signal = self.calculate_time_diff_signal(interval=interval, df=df, ticker_data=new_df.iloc[-1])
				# Get the latest timestamp from the provided DataFrame
				if signal:
					updated = True
					print(type(df))
					df = pd.concat([df, new_df], ignore_index=True)
					print(type(df))
					#Sharing_data.append_to_file(f"Data appended to DataFrame for symbol: {symbol}")

			return df, updated

		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching the ticker: {str(e)}")
			return df

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
				Sharing_data.append_to_file("Could not fetch the available balance.")
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
           
			if market_type == 'spot':
				if order_type == 'buy':
					# Fetch the ticker price to calculate max quantity
					ticker = exchange.fetch_ticker(symbol)
					price = ticker['last']
	                
					# Calculate quantity based on the percentage of available balance
					quantity = (available_balance * (percentage / 100)) / price

				elif order_type == 'sell':
					# Calculate quantity based on the percentage of available balance
					quantity = float(available_balance * (percentage / 100))

				else:
					Sharing_data.append_to_file("order_type must be 'buy' or 'sell'")

				# Ensure the quantity is within the allowed precision and limits
				quantity = max(min_order_amount, round(quantity, precision_decimal_places))

			elif market_type == 'futures':

				# Fetch the ticker price to calculate max quantity
				ticker = exchange.fetch_ticker(symbol)
				price = ticker['last']
            
				if order_type == 'buy' or order_type == 'sell': 
					# Calculate quantity based on the percentage of available balance
					min_amount = price * multiplier
					money_to_use = available_balance * (percentage / 100)
					money_really_available = self.fetch_balance(balance_currency, 'free', market_type)
					if money_really_available < money_to_use:
						money_to_use = money_really_available
					if leverage == None and min_amount > money_to_use:
						leverage = math.ceil(min_amount / money_to_use)
					elif leverage == None:
						leverage = 1
						
					quantity = (money_to_use * leverage) / (min_amount)

					# Ensure the quantity is within the allowed precision and limits
					quantity = max(1, round(quantity, precision_decimal_places))

					# Set leverage if provided and if market type is futures
					if leverage is not None and market_type == 'futures':
						params['leverage'] = leverage

				else:
					Sharing_data.append_to_file("order_type must be 'buy' or 'sell'")

			

			Sharing_data.append_to_file(f"{symbol} precision is {precision}, min_order_amount is {min_order_amount} and multiplier is {multiplier}") 
			Sharing_data.append_to_file(f"order is {order_type}, price is {price} and quantity is {quantity}")
			Sharing_data.append_to_file(f"Available balance for {balance_currency}: {available_balance}")

			# Place a market buy order
			order = exchange.create_order(symbol=symbol, type='market', side=order_type, amount=quantity, params=params)
			Sharing_data.append_to_file(f"Order placed: {order}")
			return order
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while placing the order: {str(e)}")

	def get_open_orders(self, market_type='spot'):
		# Check open orders
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			open_orders = self.exchange.fetch_open_orders('BTC/USDT')
			Sharing_data.append_to_file(f"Open orders: {open_orders}")
			return open_orders
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching open orders: {str(e)}")

	def close_position(self, symbol='BTC/USDT', market_type='spot'):
		try:
			# close a positon using only symbol as input, no order id
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			exchange.close_position(symbol = symbol)
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while trying to close order: {str(e)}")

if __name__ == "__main__":
	kucoin = Exchange(name='kucoin')
	kucoin.load_market(market_type='futures')
	kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')

	order = kucoin.place_market_order(symbol='WIFUSDTM', percentage=10, order_type='buy', market_type='futures', leverage=None, reduceOnly=False)





