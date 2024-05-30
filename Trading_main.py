from Exchange_trade import Exchange
import Trading_tools
import pandas as pd
import time

class Crypto(object):
	def __init__(self, symbol_spot=None, symbol_futures=None, leverage = None, timeframe = '1m', percentage = 20):
		self.symbol_spot = symbol_spot
		self.symbol_futures = symbol_futures
		self.df = pd.DataFrame()
		self.leverage = leverage
		self.timeframe = timeframe
		self.percentage = percentage
		# streamlit app rendering
		self.init_render = False
		self.line_chart_price = None
		self.line_chart_macd = None
		self.line_chart_df = None

class Futures_bot(object):

	def __init__(self):
		self.kucoin = Exchange(name='kucoin')
		self.binance = Exchange(name='binance')

		#crypto
		self.crypto = []
		self.crypto.append(Crypto(symbol_spot='ETH/USDT', symbol_futures='ETHUSDTM', leverage=None, timeframe='1m', percentage = 20))
		self.crypto.append(Crypto(symbol_spot='PYTH/USDT', symbol_futures='PYTHUSDTM', leverage=None, timeframe='1m', percentage = 20))
		self.crypto.append(Crypto(symbol_spot='TAO/USDT', symbol_futures='TAOUSDTM', leverage=None, timeframe='1m', percentage = 20))
		self.crypto.append(Crypto(symbol_spot='WIF/USDT', symbol_futures='WIFUSDTM', leverage=None, timeframe='1m', percentage = 20))
		self.crypto.append(Crypto(symbol_spot='ONDO/USDT', symbol_futures='ONDOUSDTM', leverage=None, timeframe='1m', percentage = 20))

		

	def run_macd_futures_trading_function(self, Crypto=None):
		start_time = time.time()
		market_type='futures'
		market_type_spot='spot'
		#print("symbol:", Crypto.symbol_spot)
		#print(f"df {Crypto.df}")

		if Crypto.df.empty:
			Crypto.df = self.binance.fetch_klines(symbol=Crypto.symbol_spot, timeframe=Crypto.timeframe, since=None, limit=200, market_type=market_type_spot)
			Crypto.df, signal_value, trend = Trading_tools.calculate_macd(Crypto.df, fast=12, slow=26, signal=9)
			Trading_tools.append_to_file(f"Crypto {Crypto.symbol_spot} dataframe created")
			print(f"Crypto {Crypto.symbol_spot} dataframe created")

		interval = self.kucoin.timeframe_to_int(interval=Crypto.timeframe)
		signal_timedelta = self.kucoin.calculate_time_diff_signal(interval=interval, df=Crypto.df, ticker_data=None)

		#print(f"Crypto {Crypto.symbol_spot} time execution {time.time() - start_time}")

		if signal_timedelta:
			#self.print = f"Crypto {Crypto.symbol_spot} Interval {Crypto.timeframe} reached, price udpated"
			Crypto.df = self.kucoin.fetch_ticker(symbol=Crypto.symbol_spot, df=Crypto.df, interval=Crypto.timeframe, market_type=market_type_spot)
			Crypto.df, signal_value, trend = Trading_tools.calculate_macd(Crypto.df, fast=12, slow=26, signal=9)
			if signal_value:
				Trading_tools.append_to_file(f"signal {signal_value} on {Crypto.symbol_spot} at time {Crypto.df['timestamp'].max()}")
				print(f"signal {signal_value} on {Crypto.symbol_spot} at time {Crypto.df['timestamp'].max()}")
				#close open order order first
				close = 'sell' if signal_value == 'buy' else 'buy'
				self.kucoin.close_position(symbol=Crypto.symbol_futures, market_type=market_type)
				self.kucoin.place_market_order(symbol=Crypto.symbol_futures, percentage=Crypto.percentage, order_type=signal_value, market_type=market_type, leverage=Crypto.leverage, reduceOnly=False)
		return Crypto

	def run_main(self):
		start_time = time.time()
		for crypto in self.crypto:
			crypto = self.run_macd_futures_trading_function(Crypto=crypto)
		#print(f"Main crypto algo time execution {time.time() - start_time}")



if __name__ == "__main__":
	Bot = Futures_bot()
	Bot.kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
	#while True:
	#	Bot.run_main()
	
	
	#Bot.kucoin.fetch_balance(currency='USDT', account='free', market_type='futures')
	#Bot.kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
	#Bot.kucoin.fetch_ticker(symbol='ETHUSDTM', interval='1m', market_type='futures')
	#Bot.kucoin.fetch_klines(symbol='ETHUSDTM', limit=200, market_type='futures')
	#Bot.kucoin.place_market_order(symbol='ETH/USDT', percentage=50, order_type='buy', market_type='spot')
	#Bot.kucoin.place_market_order(symbol='ETHUSDTM', percentage=25, order_type='buy', market_type='futures', leverage=None, reduceOnly=False)

