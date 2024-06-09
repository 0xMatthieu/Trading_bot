from Exchange_trade import Exchange
import Trading_tools
import Sharing_data
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
		# data sharing
		self.folder_path = 'data/'
		self.json_file = self.folder_path + symbol_spot.replace('/', '_') + '.json'
		self.function = None


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

		self.macd_fast = 180 #standart 12
		self.macd_slow = 390 #standart 26
		self.macd_signal = 135 #standart 9

	def update_crypto_dataframe(self, Crypto=None, function=None):
		if function == "MACD":
			Crypto.df = Trading_tools.calculate_macd(Crypto.df, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal)
		elif function == "Heikin":
			Crypto.df = Trading_tools.calculate_heikin_ashi(Crypto.df)
		Sharing_data.append_to_json(df=Crypto.df, filename=Crypto.json_file)
		return Crypto

	def run_futures_trading_function(self, Crypto=None, function=None):
		start_time = time.time()
		market_type='futures'
		market_type_spot='spot'
		Crypto.function=function #for streamlit app
		#print("symbol:", Crypto.symbol_spot)
		#print(f"df {Crypto.df}")

		if Crypto.df.empty:
			Sharing_data.erase_json_content(filename=Crypto.json_file)
			Crypto.df = self.binance.fetch_klines(symbol=Crypto.symbol_spot, timeframe=Crypto.timeframe, since=None, limit=200, market_type=market_type_spot)
			Crypto = self.update_crypto_dataframe(Crypto=Crypto, function=function)
			Sharing_data.append_to_file(f"Crypto {Crypto.symbol_spot} dataframe created for function {Crypto.function}")

		interval = self.kucoin.timeframe_to_int(interval=Crypto.timeframe)
		signal_timedelta = self.kucoin.calculate_time_diff_signal(interval=interval, df=Crypto.df, ticker_data=None)

		#print(f"Crypto {Crypto.symbol_spot} time execution {time.time() - start_time}")

		if signal_timedelta:
			print("symbol:", Crypto.symbol_spot)
			print(f"Crypto {Crypto.symbol_spot} Interval {Crypto.timeframe} reached, price udpated")
			Crypto.df = self.kucoin.fetch_ticker(symbol=Crypto.symbol_spot, df=Crypto.df, interval=Crypto.timeframe, market_type=market_type_spot)
			Crypto = self.update_crypto_dataframe(Crypto=Crypto, function=function)
			if Crypto.df['Signal'].iloc[-1]:
				Sharing_data.append_to_file(f"signal {Crypto.df['Signal'].iloc[-1]} on {Crypto.symbol_spot} at time {Crypto.df['timestamp'].max()}")
				#close open order order first (needed for buy, sell, stop loss or take profit)
				#self.kucoin.close_position(symbol=Crypto.symbol_futures, market_type=market_type)
				if Crypto.df['Signal'].iloc[-1] == 'buy' or Crypto.df['Signal'].iloc[-1] == 'sell':
					self.kucoin.close_position(symbol=Crypto.symbol_futures, market_type=market_type)
					self.kucoin.place_market_order(symbol=Crypto.symbol_futures, percentage=Crypto.percentage, order_type=Crypto.df['Signal'].iloc[-1], market_type=market_type, leverage=Crypto.leverage, reduceOnly=False)
		return Crypto

	def run_main(self):
		start_time = time.time()
		for crypto in self.crypto:
			crypto = self.run_futures_trading_function(Crypto=crypto, function="MACD")
		#print(f"Main crypto algo time execution {time.time() - start_time}")



if __name__ == "__main__":
	Bot = Futures_bot()
	Sharing_data.erase_folder_content(folder_path=Bot.crypto[0].folder_path)
	Sharing_data.append_to_file(f"Function MACD, timeframe 1m, old binance 390 180 135")
	#Bot.kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
	while True:
		Bot.run_main()
	
	
	#Bot.kucoin.fetch_balance(currency='USDT', account='free', market_type='futures')
	#Bot.kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
	#Bot.kucoin.fetch_ticker(symbol='ETHUSDTM', interval='1m', market_type='futures')
	#Bot.kucoin.fetch_klines(symbol='ETHUSDTM', limit=200, market_type='futures')
	#Bot.kucoin.place_market_order(symbol='ETH/USDT', percentage=50, order_type='buy', market_type='spot')
	#Bot.kucoin.place_market_order(symbol='ETHUSDTM', percentage=25, order_type='buy', market_type='futures', leverage=None, reduceOnly=False)

