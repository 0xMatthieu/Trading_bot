#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  3 14:11:22 2020

@author: matthieu
"""


import pandas as pd
import logging
import settings_binance as sb 
import pandas_ta as ta
import Binance_trade
	

def Get_Macd(Currency, slow, fast, signal):
	#MACD
	lon = 2
	mid = lon / 2
	slow = lon / 4
	Currency.df_macd_240 = Currency.historical.ta.macd(slow=slow, fast=fast, signal=signal, close = 'price')
	Currency.df_macd_last_value_240 = Currency.df_macd_240.iloc[-1]
	Currency.df_macd_60 = Currency.historical.ta.macd(slow=slow/mid, fast=fast/mid, signal=signal/mid, close = 'price')
	Currency.df_macd_last_value_60 = Currency.df_macd_60.iloc[-1]
	Currency.df_macd_30 = Currency.historical.ta.macd(slow=slow/slow, fast=fast/slow, signal=signal/slow, close = 'price')
	Currency.df_macd_last_value_30 = Currency.df_macd_30.iloc[-1]

def update_price_and_macd(Currency, date = 'None'):
	Init = False

	Currency.macd_status = 'Do nothing'
	Currency.current_price = Currency.price[Currency.Currency].price.iloc[-1]

	#check if price is the same
	if Currency.price['price_stuck_algo'] > 5:
		Currency.price['error'] = True
		Currency.price['price_stuck_algo'] = 0
	elif Currency.price['old_price_algo'] == Currency.current_price:
		Currency.price['price_stuck'] = Currency.price['price_stuck'] + 1
	else:
		Currency.price['price_stuck'] = 0

	Currency.price['old_price_algo'] = Currency.current_price

	if date == 'None':
		index_macd = -1 #Currency.price[Currency.Currency].index[-1]
		date = pd.Timestamp.now()
	else:
		index_macd = Currency.historical.iloc[(Currency.historical['date']-date).abs().argsort()[:1]].index.tolist()[0]
	Currency.df_macd_last_value = Currency.df_macd.iloc[index_macd]

	#init
	if Init == False:
		Init = True
		Currency.df_macd = Currency.df_macd_240.copy()

	Currency.df_macd.iloc[index_macd][1] = 0

	if Currency.df_macd_240.iloc[index_macd][1] > 0:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] + 1
	else:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] - 1

	if Currency.df_macd_60.iloc[index_macd][1] > 0:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] + 1
	else:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] - 1

	if Currency.df_macd_30.iloc[index_macd][1] > 0:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] + 1
	else:
		Currency.df_macd.iloc[index_macd][1] = Currency.df_macd.iloc[index_macd][1] - 1


	# test if signal has changed
	# if macd < signal in last cycle and macd > signal in current cycle, buy
	if Currency.df_macd.iloc[index_macd - 1][1] < 0 and Currency.df_macd.iloc[index_macd][1] > 0 and Currency.macd_status == 'Do nothing':
		Currency.macd_status = 'Buy now'
	elif Currency.df_macd.iloc[index_macd - 1][1] > 0 and Currency.df_macd.iloc[index_macd][1] < 0 and Currency.macd_status == 'Do nothing':
		Currency.macd_status = 'Sell now'
	else:
		Currency.macd_status = 'Do nothing'
	print(f"{date}: current index of {Currency.Currency_crypto} is: {Currency.df_macd.index[index_macd]}, current price is {Currency.current_price} and current MACD status is {Currency.macd_status}")
	#print(f"{date}: current MACD is: {Currency.df_macd_last_value}")
		

if __name__ == "__main__":
   main()
