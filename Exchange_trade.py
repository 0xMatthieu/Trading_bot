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
from Trading_tools import round_down

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
			return None

	def fetch_exchange_ticker(self, symbol='BTC/USDT', df=None, interval=None, market_type='spot'):
		"""Fetch ticker information for a specific symbol and append it to the provided DataFrame."""
		try:
			updated = False
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			new_df = self.fetch_klines(symbol=symbol, timeframe=interval, since=None, limit=2, market_type=market_type)
			if new_df is not None: 
			 
				if interval == None:
					df = new_df
					df.drop(df.head(1).index,inplace=True) # drop first n rows to keep only last value
					updated = True
				else:
					interval = self.timeframe_to_int(interval=interval)
					signal = self.calculate_time_diff_signal(interval=interval, df=df, ticker_data=new_df.iloc[-1])
					
					# Get the latest timestamp from the provided DataFrame
					if signal:
						df.drop(df.tail(len(new_df)-1).index,inplace=True)
						updated = True
					else:	#update last line only but doesn't return updated flag
						df.drop(df.tail(len(new_df)).index,inplace=True)
						updated = False
					df = pd.concat([df, new_df], ignore_index=True)
					#Sharing_data.append_to_file(f"Data appended to DataFrame for symbol: {symbol}")

			return df, updated

		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching the ticker: {str(e)}")
			return df, updated

		except Exception as e:
				if not new_df.empty:	#known issue when using ohlcv, no need to provide feedback
					Sharing_data.append_to_file(f"An error occurred after fetching ticker : {str(e)}")
				return df, updated

	def get_open_orders(self, symbol='BTC/USDT', market_type='spot', stop_orders=False):
		# Check open orders
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			params = {'trigger':stop_orders}
			open_orders = exchange.fetch_open_orders(symbol=symbol, params=params)
			#Sharing_data.append_to_file(f"Open orders: {open_orders}")
			return open_orders
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching open orders: {str(e)}")

	def get_position(self, symbol='BTC/USDT', market_type='spot'):
		# Check open orders
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			open_orders = exchange.fetch_position(symbol=symbol)
			#Sharing_data.append_to_file(f"Open position: {open_orders}")
			return open_orders
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while fetching open positions: {str(e)}")

	def close_position(self, symbol='BTC/USDT', market_type='spot'):
		try:
			# close a positon using only symbol as input, no order id
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
			exchange.close_position(symbol = symbol)
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while trying to close order: {str(e)}")

	def fetch_market_data(self, symbol, market_type='spot'):
		"""Fetch market data for the given symbol."""
		exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange
		return exchange.market(symbol)

	def define_stop_order_type(self, stop_order_type=None, stop_order=None, order_side=None):
		if stop_order_type is not None:
			if stop_order_type == 'take_profit_long':
				stop_order = 'up'
				order_side = 'sell'
			elif stop_order_type == 'stop_loss_long':
				stop_order = 'down'
				order_side = 'sell'
			elif stop_order_type == 'take_profit_short':
				stop_order = 'down'
				order_side = 'buy'
			elif stop_order_type == 'stop_loss_short':
				stop_order = 'up'
				order_side = 'buy'
			else:
				stop_order = None
				order_side = None
			return stop_order, order_side
		elif stop_order is not None and order_side is not None:
			if stop_order == 'up' and order_side == 'sell':
				stop_order_type = 'take_profit_long'
			elif stop_order == 'down' and order_side == 'sell':
				stop_order_type = 'stop_loss_long'
			elif stop_order == 'down' and order_side == 'buy':
				stop_order_type = 'take_profit_short'
			elif stop_order == 'up' and order_side == 'buy':
				stop_order_type = 'stop_loss_short'
			return stop_order_type


	def place_stop_order(self, symbol='BTC/USDT', quantity=100, market_type='spot', stop_order_type='take_profit_long', price=None):
		start_time = time.time()
		exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

		if price is None:
			return None

		try:
			stop_order, order_side = self.define_stop_order_type(stop_order_type=stop_order_type, stop_order=None, order_side=None)

			params = {'stop':stop_order, 'stopPriceType':'MP', 'stopPrice':price}
			# Place the order
			Sharing_data.append_to_file(f"{symbol}: stop_order_type is {stop_order_type}, params are {params} and quantity is {quantity}") 
			order = exchange.create_order(symbol=symbol, type='limit', side=order_side, price=price, amount=quantity, params=params)
			Sharing_data.append_to_file(f"Order placed: {order['id']}")
			Sharing_data.append_to_file(f"Order time execution was {time.time() - start_time}")

		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while placing the stop order: {str(e)}")

	def place_order(self, symbol='BTC/USDT', percentage=100, order_side='buy', market_type='spot', order_type='market', leverage=None):
		#percentage shall be 1 to close futures position
		
		start_time = time.time()

		if market_type == 'spot':
			base_currency, quote_currency = symbol.split('/')
		else:
			base_currency, quote_currency = symbol[:-5], 'USDT'  # Futures symbols end with 'M' (e.g., ETHUSDTM)
        
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			# define action
			if order_side == 'buy' or order_side == 'stop_loss_short' or order_side == 'take_profit_short' or order_side == 'close_short':
					side = 'buy'
			elif order_side =='sell' or order_side == 'stop_loss_long' or order_side == 'take_profit_long' or order_side == 'close_long':
					side = 'sell'


			# Fetch the available balance for the right currency
			balance_currency = base_currency if order_side == 'sell' and market_type == 'spot' else quote_currency
			balance_type = 'total' if market_type == 'futures' else 'free'
			#available_balance = self.fetch_balance(balance_currency, balance_type, market_type)
			balance_all = exchange.fetch_balance()
			available_balance = balance_all[balance_type].get(balance_currency, None)

			if available_balance is None:
				Sharing_data.append_to_file("Could not fetch the available balance.")
				return

			# Fetch market data to get the precision and limits
			market_data = self.fetch_market_data(symbol, market_type)
			precision = market_data['precision']['amount']
			min_order_amount = market_data['limits']['amount']['min']
			max_order_amount = market_data['limits']['amount']['max']
			multiplier = market_data['contractSize']	#multiplier in API, https://stackoverflow.com/questions/75522901/issue-with-kucoin-futures-api-to-create-limit-order 
			price_adjustment = market_data['precision']['price']	#needed for order limit

			# Determine the number of decimal places from the precision value
			precision_decimal_places = max(0, int(-math.log10(precision)))
			quantity = 0

			params = {'reduceOnly':False}

			price = None

			if market_type == 'spot':
				if order_side == 'buy':
					# Fetch the ticker price to calculate max quantity
					ticker = exchange.fetch_tickerfetch_ticker(symbol)
					price = ticker['last']
	                
					# Calculate quantity based on the percentage of available balance
					quantity = (available_balance * (percentage / 100)) / price

				elif order_side == 'sell':
					# Calculate quantity based on the percentage of available balance
					quantity = float(available_balance * (percentage / 100))

				else:
					Sharing_data.append_to_file("side must be 'buy' or 'sell'")

				# Ensure the quantity is within the allowed precision and limits
				quantity = max(min_order_amount, round_down(quantity, precision_decimal_places))

			elif market_type == 'futures':
				ticker = exchange.fetch_ticker(symbol)

				if order_type == 'market':
					# Fetch the ticker price to calculate max quantity
					price = ticker['last']
				elif order_type == 'limit':
					# Fetch the current order book
					order_book = exchange.fetch_order_book(symbol)
					if order_side == 'buy' or order_side == 'close_short' or order_side == 'stop_loss_short' or order_side == 'take_profit_short':
						# Place a limit buy order slightly above the best bid
						best_order_book = order_book['bids'][1][0]
						best_order_book_ticker = float(ticker['info']['bestAskPrice'])
						price = best_order_book + 1 * price_adjustment
					elif order_side == 'sell' or order_side == 'close_long' or order_side == 'stop_loss_long' or order_side == 'take_profit_long':
						# Place a limit sell order slightly below the best ask
						best_order_book = order_book['asks'][1][0]
						best_order_book_ticker = float(ticker['info']['bestBidPrice'])
						price = best_order_book - 1 * price_adjustment
            
				if order_side == 'buy' or order_side == 'sell':

					##########
					# TODO to improve but current solution to not block
					# TODO calculate the position price and update money_really_available with the position still open, should fix it
					self.close_position(symbol=symbol, market_type=market_type)
					##########

					
					# Calculate quantity based on the percentage of available balance
					min_amount = price * multiplier
					money_to_use = available_balance * (percentage / 100)
					money_really_available = balance_all['free'].get(balance_currency, None)
					if money_really_available < money_to_use:
						money_to_use = money_really_available
					if leverage == None and min_amount > money_to_use:
						leverage = math.ceil(min_amount / money_to_use)
					elif leverage == None:
						leverage = 1
						
					quantity = (money_to_use * leverage) / (min_amount)

					# Ensure the quantity is within the allowed precision and limits
					quantity = max(1, round_down(quantity, precision_decimal_places))

				# if there is already an open order, add quantity of order to close
				open_order = self.get_position(symbol=symbol, market_type=market_type)
				if open_order['contracts'] is not None:
					if ((open_order['side'] == 'long' and order_side == 'sell') or (open_order['side'] == 'short' and order_side == 'buy')
					or order_side == 'close_long' or order_side == 'stop_loss_long' or order_side == 'take_profit_long'
					or order_side == 'close_short' or order_side == 'stop_loss_short' or order_side == 'take_profit_short'):
						quantity = quantity + open_order['contracts']

				# Set leverage if provided and if market type is futures
				if leverage is not None and market_type == 'futures':
					params['leverage'] = leverage

				if (order_side == 'close_long' or order_side == 'stop_loss_long' or order_side == 'take_profit_long'
				or order_side == 'close_short' or order_side == 'stop_loss_short' or order_side == 'take_profit_short'):
					#params['closeOrder'] = True
					params['reduceOnly'] = True

			Sharing_data.append_to_file(f"{symbol}: precision is {precision}, min_order_amount is {min_order_amount} and multiplier is {multiplier}") 
			Sharing_data.append_to_file(f"order is {order_type}, side was {order_side} so executed as {side}. Price is {price} quantity is {quantity} and leverage is {leverage}")
			if order_type == 'limit':
				Sharing_data.append_to_file(f"Order book price found was {best_order_book}. Best ticker was {best_order_book}. Last price was {ticker['last']}")
				Sharing_data.append_to_file(f"Open order was {open_order['side']} for a size of {open_order['contracts']}")
			Sharing_data.append_to_file(f"Available balance for {balance_currency}: {available_balance}")
			if market_type == 'futures' and (order_side == 'buy' or order_side == 'sell'):
				Sharing_data.append_to_file(f"Money really available for {balance_currency}: {money_really_available}")
			# Place the order
			order = exchange.create_order(symbol=symbol, type=order_type, side=side, price=price, amount=quantity, params=params)
			Sharing_data.append_to_file(f"Order placed: {order['id']}")
			Sharing_data.append_to_file(f"Order time execution was {time.time() - start_time}")
			return quantity
		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while placing the order: {str(e)}")

	def create_stop_orders(self, symbol='BTC/USDT', signal=None, stop_loss_long_price=None, take_profit_long_price=None, 
		stop_loss_short_price=None, take_profit_short_price=None, market_type='spot', quantity=None):
		"""
		Create both take profit and stop loss stop orders 
		"""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			# Fetch the current order status
			orders = self.get_open_orders(symbol=symbol, market_type=market_type, stop_orders=True)

			if orders: #means not empty
				for order in orders:    
					# Cancel the current order if not filled
					Sharing_data.append_to_file(f"Order {order['id']} canceled for adjustment.")
					exchange.cancel_order(order['id'], symbol)
			
			if signal == 'buy': # means long
				self.place_stop_order(symbol=symbol, quantity=quantity, market_type=market_type, stop_order_type='take_profit_long', price=take_profit_long_price)
				self.place_stop_order(symbol=symbol, quantity=quantity, market_type=market_type, stop_order_type='stop_loss_long', price=stop_loss_long_price)
			elif signal == 'sell': # means short
				self.place_stop_order(symbol=symbol, quantity=quantity, market_type=market_type, stop_order_type='take_profit_short', price=take_profit_short_price)
				self.place_stop_order(symbol=symbol, quantity=quantity, market_type=market_type, stop_order_type='stop_loss_short', price=stop_loss_short_price)

		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while creating stop orders: {str(e)}")

	def monitor_and_adjust_stop_orders(self, symbol='BTC/USDT', stop_loss_long_price=None, take_profit_long_price=None, 
		stop_loss_short_price=None, take_profit_short_price=None, market_type='spot'):
		"""
		Monitor and adjust the stop orders to update stop loss and take profit
		"""
		try:
			exchange = self.spot_exchange if market_type == 'spot' else self.futures_exchange

			# check if there is an open position 
			open_position = self.get_position(symbol=symbol, market_type=market_type)

			# Fetch the current order status
			orders = self.get_open_orders(symbol=symbol, market_type=market_type, stop_orders=True)

			if not orders or not open_position:
				return None	#means no open order or position has been closed,, empty list

			for order in orders:
				order_side = order['info']['side']
				stop_order = order['info']['stop']
				quantity = order['remaining']
				current_price = order['price']

				stop_order_type = self.define_stop_order_type(stop_order_type=None, stop_order=stop_order, order_side=order_side)

				# compare price set with price calculated, if different: cancel order and create a new one
				if stop_order_type == 'take_profit_long':
					price = take_profit_long_price
				elif stop_order_type == 'take_profit_short':
					price = take_profit_short_price
				if stop_order_type == 'stop_loss_long':
					price = stop_loss_long_price
				elif stop_order_type == 'stop_loss_short':
					price = stop_loss_short_price

				if current_price != price:     
					# Cancel the current order if not filled
					Sharing_data.append_to_file(f"Order {order['id']} canceled for adjustment.")
					exchange.cancel_order(order['id'], symbol)
					self.place_stop_order(symbol=symbol, quantity=quantity, market_type=market_type, stop_order_type=stop_order_type, price=price)

		except ccxt.BaseError as e:
			Sharing_data.append_to_file(f"An error occurred while monitoring stop orders: {str(e)}")

if __name__ == "__main__":
	kucoin = Exchange(name='kucoin')
	kucoin.load_market(market_type='futures')
	kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')

	order = kucoin.place_market_order(symbol='WIFUSDTM', percentage=10, order_type='buy', market_type='futures', leverage=None, reduceOnly=False)





