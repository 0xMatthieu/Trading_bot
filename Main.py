#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 14:11:22 2020

@author: matthieu
"""

import settings_binance as sb
import Binance_trade
import Trade_algo
import Third_algo
import time
import logging
import pandas as pd

""""
remove comments in binance_trade before sarting, to get money
"""

sb.init()
sb.do_real_order = False
sb.total_money_available = 1400
sb.total_money_available_futures = 1286
Start_date = "20 days ago UTC"
Start_date_delta = "1 minute ago UTC"
Algo_step = 60
Cycle_step = 60
Macd_step = 60*60*2400 #every 2400hours
Time_algo = time.time() + Algo_step
Time_cycle = time.time() + Cycle_step
Time_macd = time.time() + Macd_step

#crypto

Currency1 = sb.Currency('BTCUSDT', 'BTC')
Currency2 = sb.Currency('BNBUSDT', 'BNB')
Currency3 = sb.Currency('ETHUSDT', 'ETH')
Currency4 = sb.Currency('AVAXUSDT', 'AVAX')
Currency5 = sb.Currency('SANDUSDT', 'SAND')
Currency6 = sb.Currency('LTCUSDT', 'LTC')
Currency7 = sb.Currency('ADAUSDT', 'ADA')
Currency8 = sb.Currency('MATICUSDT', 'MATIC')
Currency9 = sb.Currency('KSMUSDT', 'KSM')
Currency10 = sb.Currency('CRVUSDT', 'CRV')
Currency1.percentage = 0.098
Currency2.percentage = 0.098
Currency3.percentage = 0.098
Currency4.percentage = 0.098
Currency5.percentage = 0.098
Currency6.percentage = 0.098
Currency7.percentage = 0.098
Currency8.percentage = 0.098
Currency9.percentage = 0.098
Currency10.percentage = 0.098

#get historical value, needed for MACD
sample = 2*60 #4h
slow=26 * sample
fast=12 * sample
signal=9 * sample

Binance_trade.get_historical_data(Currency = Currency1, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency2, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency3, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency4, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency5, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency6, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency7, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency8, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency9, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
Binance_trade.get_historical_data(Currency = Currency10, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)

Trade_algo.Get_Macd(Currency1, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency2, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency3, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency4, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency5, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency6, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency7, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency8, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency9, slow=slow, fast=fast, signal=signal)
Trade_algo.Get_Macd(Currency10, slow=slow, fast=fast, signal=signal)

# init API to start to get data on defined crypto
Binance_trade.start_to_get_data(Currency1)
Binance_trade.start_to_get_data(Currency2)
Binance_trade.start_to_get_data(Currency3)
Binance_trade.start_to_get_data(Currency4)
Binance_trade.start_to_get_data(Currency5)
Binance_trade.start_to_get_data(Currency6)
Binance_trade.start_to_get_data(Currency7)
Binance_trade.start_to_get_data(Currency8)
Binance_trade.start_to_get_data(Currency9)
Binance_trade.start_to_get_data(Currency10)

Binance_trade.get_currency_min_notional(Currency1)
Binance_trade.get_currency_min_notional(Currency2)
Binance_trade.get_currency_min_notional(Currency3)
Binance_trade.get_currency_min_notional(Currency4)
Binance_trade.get_currency_min_notional(Currency5)
Binance_trade.get_currency_min_notional(Currency6)
Binance_trade.get_currency_min_notional(Currency7)
Binance_trade.get_currency_min_notional(Currency8)
Binance_trade.get_currency_min_notional(Currency9)
Binance_trade.get_currency_min_notional(Currency10)

sb.order_done_current_cycle = True
#Binance_trade.money_available(Log = sb.order_done_current_cycle, Currency1 = Currency1, Currency2 = Currency2, Currency3 = Currency3, Currency4 = Currency4, Currency5= Currency5)
Binance_trade.futures_fiat_available(Log = sb.order_done_current_cycle)

logging.critical(f" ---------------------------------------------------------------------")
logging.critical(f" ----------------------------- start software ------------------------")
logging.critical(f" ---------------------------------------------------------------------")
logging.critical(f" MACD {slow} {fast} {signal}")

while True:

	if time.time() > Time_cycle:
		Time_cycle = time.time() + Cycle_step
		sb.order_done_current_cycle = False
		Binance_trade.get_current_data(Currency1)
		Binance_trade.get_current_data(Currency2)
		Binance_trade.get_current_data(Currency3)
		Binance_trade.get_current_data(Currency4)
		Binance_trade.get_current_data(Currency5)
		Binance_trade.get_current_data(Currency6)
		Binance_trade.get_current_data(Currency7)
		Binance_trade.get_current_data(Currency8)
		Binance_trade.get_current_data(Currency9)
		Binance_trade.get_current_data(Currency10)


		if Currency1.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency1)
			Third_algo.buy_function_futures(Currency1)
			Third_algo.sell_function_futures(Currency1)
		
		if Currency2.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency2)
			Third_algo.buy_function_futures(Currency2)
			Third_algo.sell_function_futures(Currency2)

		if Currency3.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency3)
			Third_algo.buy_function_futures(Currency3)
			Third_algo.sell_function_futures(Currency3)

		if Currency4.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency4)
			Third_algo.buy_function_futures(Currency4)
			Third_algo.sell_function_futures(Currency4)

		if Currency5.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency5)
			Third_algo.buy_function_futures(Currency5)
			Third_algo.sell_function_futures(Currency5)

		if Currency6.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency6)
			Third_algo.buy_function_futures(Currency6)
			Third_algo.sell_function_futures(Currency6)
		
		if Currency7.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency7)
			Third_algo.buy_function_futures(Currency7)
			Third_algo.sell_function_futures(Currency7)

		if Currency8.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency8)
			Third_algo.buy_function_futures(Currency8)
			Third_algo.sell_function_futures(Currency8)

		if Currency9.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency9)
			Third_algo.buy_function_futures(Currency9)
			Third_algo.sell_function_futures(Currency9)

		if Currency10.price['error'] == False:
			Trade_algo.update_price_and_macd(Currency10)
			Third_algo.buy_function_futures(Currency10)
			Third_algo.sell_function_futures(Currency10)

		Binance_trade.futures_fiat_available(Log = sb.order_done_current_cycle)
		#Binance_trade.money_available(Log = sb.order_done_current_cycle, Currency1 = Currency1, Currency2 = Currency2, Currency3 = Currency3, Currency4 = Currency4, Currency5= Currency5)

	#historical
	if time.time() > Time_macd:
		Time_macd = time.time() + Macd_step
		Binance_trade.get_historical_data(Currency = Currency1, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency2, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency3, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency4, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency5, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency6, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency7, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency8, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency9, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
		Binance_trade.get_historical_data(Currency = Currency10, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)

		Trade_algo.Get_Macd(Currency1, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency2, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency3, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency4, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency5, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency6, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency7, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency8, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency9, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency10, slow=slow, fast=fast, signal=signal)

	#get historical value, needed for MACD
	if time.time() > Time_algo:
		Time_algo = time.time() + Algo_step
		Currency1.historical = Currency1.historical.append(Currency1.price[Currency1.Currency].iloc[-1], ignore_index=True)
		Currency2.historical = Currency2.historical.append(Currency2.price[Currency2.Currency].iloc[-1], ignore_index=True)
		Currency3.historical = Currency3.historical.append(Currency3.price[Currency3.Currency].iloc[-1], ignore_index=True)
		Currency4.historical = Currency4.historical.append(Currency4.price[Currency4.Currency].iloc[-1], ignore_index=True)
		Currency5.historical = Currency5.historical.append(Currency5.price[Currency5.Currency].iloc[-1], ignore_index=True)
		Currency6.historical = Currency6.historical.append(Currency6.price[Currency6.Currency].iloc[-1], ignore_index=True)
		Currency7.historical = Currency7.historical.append(Currency7.price[Currency7.Currency].iloc[-1], ignore_index=True)
		Currency8.historical = Currency8.historical.append(Currency8.price[Currency8.Currency].iloc[-1], ignore_index=True)
		Currency9.historical = Currency9.historical.append(Currency9.price[Currency9.Currency].iloc[-1], ignore_index=True)
		Currency10.historical = Currency10.historical.append(Currency10.price[Currency10.Currency].iloc[-1], ignore_index=True)
				
		Trade_algo.Get_Macd(Currency1, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency2, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency3, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency4, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency5, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency6, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency7, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency8, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency9, slow=slow, fast=fast, signal=signal)
		Trade_algo.Get_Macd(Currency10, slow=slow, fast=fast, signal=signal)

	#time.sleep(10)


# properly stop and terminate WebSocket
#sb.twm.stop()

