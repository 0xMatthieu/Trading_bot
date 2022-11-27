#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 14:11:22 2020

@author: matthieu
"""


import time

from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceWebsocketUnableToConnect
from binance import ThreadedWebsocketManager, Client
import pandas as pd
import logging
import settings_binance as sb 
import math

logging.basicConfig(filename='my_log_file.log', format='%(asctime)s - %(message)s', level=logging.INFO)

print ('program run')

logging.info(f" start program at : {pd.Timestamp.now()}")

def get_historical_data(Currency, Interval = Client.KLINE_INTERVAL_1DAY, Start_date = "40 days ago UTC"):
	#get historical data of last days
	try:
		sb.client = Client(sb.api_key, sb.api_secret)
		klines = sb.client.get_historical_klines(Currency.Currency, Interval, Start_date)
		for line in klines:
			del line[5:]
			del line[1]
		for line in klines:
			#del line[1:4]
			del line[1:3]
		Currency.historical = pd.DataFrame(klines, columns=['date', 'price'])
		Currency.historical['price'] = pd.to_numeric(Currency.historical['price'])
		Currency.historical.date = pd.to_datetime(Currency.historical.date, unit='ms')
		#return dataframe
	except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency_crypto}: BinanceAPIException during klines historical access: {e}")


def get_historical_data_csv(Currency, Interval = Client.KLINE_INTERVAL_1DAY, Start_date = "365 days ago UTC"):
	#get historical data of last days
	try:
		sb.client = Client(sb.api_key, sb.api_secret)
		klines = sb.client.get_historical_klines(Currency.Currency, Interval, Start_date)
		for line in klines:
			del line[6:]
		Currency.historical = pd.DataFrame(klines, columns=['Date','Open','High','Low','Close','Volume'])
		Currency.historical['Adj Close'] = Currency.historical['Close']
		Currency.historical = Currency.historical[['Date','Open','High','Low','Close','Adj Close','Volume']]
		Currency.historical['Open'] = pd.to_numeric(Currency.historical['Open'])
		Currency.historical['High'] = pd.to_numeric(Currency.historical['High'])
		Currency.historical['Low'] = pd.to_numeric(Currency.historical['Low'])
		Currency.historical['Close'] = pd.to_numeric(Currency.historical['Close'])
		Currency.historical['Adj Close'] = pd.to_numeric(Currency.historical['Adj Close'])
		Currency.historical['Volume'] = pd.to_numeric(Currency.historical['Volume'])
		Currency.historical.Date = pd.to_datetime(Currency.historical.Date, unit='ms')
		#Currency.historical.to_csv('Ada_day_last_365_days', index=False)
		#return dataframe
	except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency_crypto}: BinanceAPIException during klines historical access: {e}")

def start_to_get_data(Currency):
	# start is required to initialise its internal loop
	Currency.twm = ThreadedWebsocketManager(api_key=sb.api_key, api_secret=sb.api_secret)
	Currency.twm.start()
	
	def btc_pairs_trade(msg):
		''' define how to process incoming WebSocket messages '''
		if msg['e'] != 'error':

			#print(f"{pd.Timestamp.now()}: websocket price of {Currency.Currency_crypto} is: {float(msg['k']['c'])} while current price is {Currency.current_price}")
			Currency.price[Currency.Currency].loc[len(Currency.price[Currency.Currency])] = [pd.Timestamp.now(), float(msg['k']['c'])]

			#check if price is the same
			if Currency.price['price_stuck'] > 20:
				Currency.price['error'] = True
				Currency.price['price_stuck'] = 0
			elif Currency.price['old_price'] == float(msg['k']['c']):
				Currency.price['price_stuck'] = Currency.price['price_stuck'] + 1
			else:
				Currency.price['price_stuck'] = 0
		else:
			Currency.price['error'] = True

		Currency.price['old_price'] = float(msg['k']['c'])
		
	# init and start the WebSocket
	Currency.twm.start_kline_socket(callback=btc_pairs_trade, symbol=Currency.Currency, interval=sb.Client.KLINE_INTERVAL_1MINUTE)

	## main
	while len(Currency.price[Currency.Currency]) == 0:
		# wait for WebSocket to start streaming data
		time.sleep(0.1)


def get_current_data(Currency):
	# error check to make sure WebSocket is working
	if Currency.price['error']:
		# stop and restart socket
		Currency.twm.stop()
		time.sleep(1)

		logging.critical(f" -------------------------------error--------------------------------------")
		logging.critical(f" at {pd.Timestamp.now()} {Currency.Currency} price error futures")
		Currency.price['error'] = False

		start_to_get_data(Currency)


def define_futures_quantity(Currency):
	sb.order_done_current_cycle = True
	futures_fiat_available(Log = sb.order_done_current_cycle)

	quantity = round(sb.asset_futures * Currency.percentage * Currency.leverage / Currency.current_price, Currency.precision)

	margin = quantity * Currency.current_price / Currency.leverage

	if margin > sb.current_money_available_futures:
		logging.error(f" {Currency.Currency}: quantity is {quantity}, which leads to higher margin than {sb.current_money_available_futures}")
		print(f" {Currency.Currency}: quantity is {quantity}, which leads to higher margin than {sb.current_money_available_futures}")

		quantity = round(sb.current_money_available_futures * 0.95 * Currency.leverage / Currency.current_price, Currency.precision)

		logging.error(f" {Currency.Currency}: new quantity is {quantity} ")
		print(f" {Currency.Currency}: new quantity is {quantity} ")

	return quantity

def do_futures_order(Currency, order_type = "None", quantity = 0, leverage = 4):
	#fee = 0.001 * quantity
	#quantity = max(round(quantity - fee, 0), 0)
	if sb.do_real_order:
		"""
		try:
			sb.client.futures_change_margin_type(symbol=Currency.Currency, marginType='ISOLATED')
		except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency_crypto}: BinanceAPIException {e}")
		"""
		ReduceOnly = True if order_type == "Long_sell" or order_type == "Short_sell" else False
		try:
			sb.client.futures_change_leverage(symbol=Currency.Currency, leverage=leverage)
		except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency}: BinanceAPIException {e}")
		try:
			if order_type == "Long_buy" or order_type == "Short_sell":
				order = sb.client.futures_create_order(symbol=Currency.Currency, side='BUY', type='MARKET', quantity=quantity, isolated=False, reduceOnly = ReduceOnly)
				logging.critical(f"{Currency.Currency_crypto}: real buy order done, struct is {order}")
			elif order_type == "Short_buy" or order_type == "Long_sell":
				order = sb.client.futures_create_order(symbol=Currency.Currency, side='SELL', type='MARKET', quantity=quantity, isolated=False, reduceOnly = ReduceOnly)
				logging.critical(f"{Currency.Currency_crypto}: real sell order done, struct is {order}")
			else:
				return
		except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency}: BinanceAPIException {e}")
		except BinanceOrderException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency}: BinanceOrderException {e}")
	else:
		logging.critical(f"{Currency.Currency_crypto}:fake order {order_type} done for a quantity of {quantity} {Currency.Currency_crypto}")
		print(f"{Currency.Currency_crypto}:fake order {order_type} done for a quantity of {quantity} {Currency.Currency_crypto}")
		if order_type == "Long_buy":
			#long
			sb.current_money_available_futures = max(sb.current_money_available_futures - quantity, 0)
			Currency.current_crypto_available = Currency.current_crypto_available + quantity
			Currency.futures_long_price = Currency.current_price
			Currency.current_future = 'Long'
		elif order_type == "Long_sell":
			#long
			if Currency.futures_long_price != 0:
				delta = Currency.current_price / Currency.futures_long_price - 1
				position = 1 + delta * leverage
				sb.current_money_available_futures = sb.current_money_available_futures + quantity * position
				Currency.current_crypto_available = max(Currency.current_crypto_available - quantity, 0)
				Currency.current_future = 'None'
				sb.balance = sb.current_money_available_futures - sb.total_money_available_futures
				logging.warning(f"{Currency.Currency_crypto}: DEBUG: delta is {delta}, position {position} and entry price {Currency.futures_long_price}")

		if order_type == "Short_buy":
			#short
			Currency.futures_short_price = Currency.current_price
			sb.current_money_available_futures = max(sb.current_money_available_futures - quantity, 0)
			Currency.current_crypto_available = Currency.current_crypto_available + quantity
			Currency.current_future = 'Short'
		elif order_type == "Short_sell":
			#short
			if Currency.futures_short_price != 0:
				delta = Currency.futures_short_price / Currency.current_price - 1
				position = 1 + delta * leverage
				sb.current_money_available_futures = sb.current_money_available_futures + quantity * position
				Currency.current_crypto_available = max(Currency.current_crypto_available - quantity, 0)
				Currency.current_future = 'None'
				sb.balance = sb.current_money_available_futures - sb.total_money_available_futures
				logging.warning(f"{Currency.Currency_crypto}: DEBUG: delta is {delta}, position {position} and entry price {Currency.futures_short_price}")

def futures_fiat_available(Log = False):
	# shall be call first, reset current total
	if sb.api_key != None and sb.test == False and Log == True:
		try:
			#time.sleep(0.01)
			value = sb.client.futures_account_balance()
			for x in value:
				if x['asset'] == 'USDT':
					sb.asset_futures = float(x['balance'])
					sb.current_money_available_futures = float(x['withdrawAvailable'])
		except BinanceAPIException as e:
			# error handling goes here
			logging.error(f"{Currency.Currency_crypto}: BinanceAPIException during asset balance access: {e}")
		except BinanceWebsocketUnableToConnect as e:
			logging.error(f"{Currency.Currency_crypto}: BinanceWebsocketUnableToConnect during asset balance access: {e}")
	sb.balance_futures = round(sb.asset_futures - sb.total_money_available_futures, 2)
	if Log == True:
		logging.info(f" money available is {sb.asset_futures} EUR, withdraw available is {sb.current_money_available_futures}")
		logging.info(f" balance futures is {sb.balance_futures} EUR")
		print(f" money available is {sb.asset_futures} EUR, withdraw available is {sb.current_money_available_futures}")
		print(f" balance futures is {sb.balance_futures} EUR")

def get_currency_min_notional(Currency):
	info = sb.client.get_symbol_info(Currency.Currency)
	Currency.min_notional = float(info['filters'][3]['minNotional'])
	StepSize = float(info['filters'][2]['stepSize'])
	Currency.precision = int(round(-math.log(StepSize, 10), 0))
	Currency.precision = Currency.precision - 2 #found on internet, doesn't make sense ...
	if Currency.precision < 0:
		Currency.precision = 0
	Currency.qty_reduce_only = round(float(info['filters'][5]['maxQty'])/100, 0)

if __name__ == "__main__":
   main()
