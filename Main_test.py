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
import matplotlib.pyplot as plt
import math
from random import randrange

sb.init()
sb.do_real_order = False
sb.test = True
Draw = True

Start_date = "100 days ago UTC"
Start_date_historical = "100 days ago UTC"

#crypto
Ada = sb.Currency('ADAUSDT', 'ADA')
#Eth = sb.Currency('ETHEUR', 'ETH')


#get historical value, needed for MACD and others ...
#Binance_trade.get_historical_data(Currency = Ada, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)
#Binance_trade.get_historical_data(Currency = Ada, Interval = sb.Client.KLINE_INTERVAL_5MINUTE, Start_date = Start_date_historical)
#Binance_trade.get_historical_data(Currency = Eth, Interval = sb.Client.KLINE_INTERVAL_1MINUTE, Start_date = Start_date)

#save
#json = Ada.historical.to_json('Ada_historical_100.json', orient = "records")
#json = Eth.historical.to_json('Eth_historical_200.json', orient = "records")


#read
Ada.historical = pd.read_json('Ada_historical_100.json')
Ada.historical_price = Ada.historical
#Eth.historical = pd.read_json('Eth_historical_200.json')
#Eth.historical_price = Eth.historical

Binance_trade.get_currency_min_notional(Ada)
#Binance_trade.get_currency_min_notional(Eth)

#Binance_trade.money_available(Log = sb.order_done_current_cycle, Currency1 = Ada)#, Currency2 = Eth)




if Draw:
	#plt.ion()
	#ax = plt.gca()
	df_Ada = pd.DataFrame(columns=['date', 'Balance', 'price', 'macd'])


Ada.balance = 0
Ada.current_crypto_available = 0 #ADA
sb.total_money_available = 1000
sb.current_money_available = sb.total_money_available
sb.total_money_available_futures = 1000
sb.current_money_available_futures = 1000 
sb.asset_futures = 1000

sample = 2*60 #2h

fast = 12 * sample
slow = 26 * sample
signal = 9 * sample


Trade_algo.Get_Macd(Ada, fast=fast, slow=slow, signal=signal)
#Trade_algo.Get_Macd(Eth, fast=75, slow=300, signal=60)
Ada.df_macd = Ada.df_macd_240.copy()

Init = False
for row in Ada.df_macd.itertuples():
	if Init == False:
		Init = True
		last_macd = row
		#last_macd_eth = Eth.df_macd.iloc[row[0]]
	else:

		index_macd = row[0]
		Ada.df_macd.iloc[index_macd][1] = 0

		if Ada.df_macd_240.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		if Ada.df_macd_60.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		if Ada.df_macd_30.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		print(f"date : {Ada.historical_price.date.iloc[row[0]]}, 120: {Ada.df_macd_240.iloc[index_macd][1]}, 60: {Ada.df_macd_60.iloc[index_macd][1]}, 30: {Ada.df_macd_30.iloc[index_macd][1]}, total: {Ada.df_macd.iloc[index_macd][1]}")

Init = False
for row in Ada.df_macd.itertuples():
	if Init == False:
		Init = True
		last_macd = row
		#last_macd_eth = Eth.df_macd.iloc[row[0]]
	else:

		index_macd = row[0]
		Ada.df_macd.iloc[index_macd][1] = 0

		if Ada.df_macd_240.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		if Ada.df_macd_60.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		if Ada.df_macd_30.iloc[index_macd][1] > 0:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] + 1
		else:
			Ada.df_macd.iloc[index_macd][1] = Ada.df_macd.iloc[index_macd][1] - 1

		# test if signal has changed
		# if macd < signal in last cycle and macd > signal in current cycle, buy
		if Ada.df_macd.iloc[index_macd-1][1] < 0 and Ada.df_macd.iloc[index_macd][1] > 0 and Ada.macd_status == 'Do nothing':
			Ada.macd_status = 'Buy now'
			stat = 30
		elif Ada.df_macd.iloc[index_macd-1][1] > 0 and Ada.df_macd.iloc[index_macd][1] < 0 and Ada.macd_status == 'Do nothing':
			Ada.macd_status = 'Sell now'
			stat = 10
		else:
			Ada.macd_status = 'Do nothing'
			stat = 0

		last_macd = row
		"""
		Ada.df_macd_last_value[0] = row[1]
		Ada.df_macd_last_value[1] = row[2]
		Ada.df_macd_last_value[2] = row[3]
		"""

		if Ada.macd_status != 'Do nothing':# or Ada.df_rsi_last_value > 70:
			print(f"MACD status is {Ada.macd_status} and macd value is {Ada.df_macd.iloc[index_macd][1]}")
			
			Ada.price[Ada.Currency].loc[len(Ada.price[Ada.Currency])] = [Ada.historical_price.date.iloc[row[0]], Ada.historical_price.price.iloc[row[0]]]
			Ada.current_price = Ada.price[Ada.Currency].price.iloc[-1]
			Third_algo.buy_function_futures(Ada)
			Third_algo.sell_function_futures(Ada)
		
			#Binance_trade.money_available(Log = sb.order_done_current_cycle, Currency1 = Ada)#, Currency2 = Eth)
			print(f"Money is {sb.current_money_available_futures}")
			

			if Draw:
				df_Ada.loc[len(df_Ada)] = [Ada.historical_price.date.iloc[row[0]], sb.balance, Ada.current_price, stat]
		"""
		# if macd < signal in last cycle and macd > signal in current cycle, buy
		if last_macd_eth[0] < last_macd_eth[2] and Eth.df_macd.iloc[row[0]][0] > Eth.df_macd.iloc[row[0]][2]:
			Eth.macd_status = 'Buy now'
		elif last_macd_eth[0] > last_macd_eth[2] and Eth.df_macd.iloc[row[0]][0] < Eth.df_macd.iloc[row[0]][2]:
			Eth.macd_status = 'Sell now'
		else:
			Eth.macd_status = 'Do nothing'

		last_macd_eth = Eth.df_macd.iloc[row[0]]

		if Eth.macd_status != 'Do nothing':

			Eth.price[Eth.Currency].loc[len(Eth.price[Eth.Currency])] = [Eth.historical_price.date.iloc[row[0]], Eth.historical_price.price.iloc[row[0]]]
			Eth.current_price = Eth.price[Eth.Currency].price.iloc[-1]
			Third_algo.buy_or_sell(Eth)
			Third_algo.buy_function(Eth)
			Third_algo.sell_function(Eth)
		
			Binance_trade.money_available(Log = sb.order_done_current_cycle, Currency1 = Ada, Currency2 = Eth)
		"""
if Draw:
	#ax.clear()
	#plt.figure()
	
	ax = df_Ada.plot(kind='line',x='date',y='Balance', color ='r')
	#df_Ada.plot(kind='line',x='date',y='macd', color ='g', ax=ax)
	ax.set_xlabel('MACD: fast={0}, slow={1}, signal={2}' .format(fast, slow, signal))
	ax2 = ax.twinx()
	df_Ada.plot(kind='line',x='date',y='price', color = 'b', ax=ax2)
	#plt.xticks(df['date'])
	#plt.draw()

plt.show()

print(f"buy trade is {Ada.benefit_buy} : {Ada.buy_good_trade} / {Ada.buy_bad_trade}, sell trade is {Ada.benefit_sell} : {Ada.sell_good_trade} / {Ada.sell_bad_trade}")


if Draw:
	#ax.clear()
	ax = df_Ada.plot(kind='line',x='date',y='Balance', color ='r')
	ax2 = ax.twinx()
	df_Ada.plot(kind='line',x='date',y='price', color = 'b', ax=ax2)
	#plt.xticks(df['date'])
	#plt.draw()
	plt.show()




