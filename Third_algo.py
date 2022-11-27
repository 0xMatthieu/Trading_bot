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
import numpy as np
import time


def buy_function_futures(Currency):
	# check if there is money available
	if Currency.current_future != 'Long':
		if Currency.macd_status == 'Buy now':
			logging.critical(f" ---------------------------------------------------------------------")
			logging.critical(f" at {Currency.price[Currency.Currency].date.iloc[-1]}: price of {Currency.Currency} is {Currency.current_price}, last price is {Currency.last_price} and status is {Currency.macd_status}")
			logging.critical(f" crypto has been bought")
			print(f"{Currency.price[Currency.Currency].date.iloc[-1]}: price of {Currency.Currency} is {Currency.current_price}and status is {Currency.macd_status}")		
			order_quantity_futures(Currency = Currency, order_type = "Buy", percentage = Currency.percentage)


def sell_function_futures(Currency):
	# check if there is crypto available
	if Currency.current_future != 'Short':
		if Currency.macd_status == 'Sell now':
			# do order and write in log
			logging.critical(f" ---------------------------------------------------------------------")
			logging.critical(f" at {Currency.price[Currency.Currency].date.iloc[-1]}: price of {Currency.Currency} is {Currency.current_price}, last price is {Currency.last_price} and status is {Currency.macd_status}")
			logging.critical(f" crypto has been sell")
			print(f"{Currency.price[Currency.Currency].date.iloc[-1]}: price of {Currency.Currency} is {Currency.current_price} and status is {Currency.macd_status}")
			order_quantity_futures(Currency = Currency, order_type = "Sell", percentage = Currency.percentage)

def order_quantity_futures(Currency, order_type = "None", percentage = 0):


	if order_type == "Buy":
		#place real order
		logging.error(f"{Currency.Currency_crypto}: short sell")
		Binance_trade.do_futures_order(Currency = Currency, order_type = "Short_sell", quantity = Currency.qty_reduce_only, leverage = Currency.leverage)

		time.sleep(1)
		quantity = Binance_trade.define_futures_quantity(Currency = Currency)
		logging.warning(f"{Currency.Currency_crypto}: DEBUG: quantity {quantity} and percentage {percentage}")
		time.sleep(1)

		#place real order
		logging.error(f"{Currency.Currency_crypto}: long buy")
		Binance_trade.do_futures_order(Currency = Currency, order_type = "Long_buy", quantity = quantity, leverage = Currency.leverage)
		Currency.last_qty_order_futures = quantity

	elif order_type == "Sell":
		#place real order
		logging.error(f"{Currency.Currency_crypto}: long sell")
		Binance_trade.do_futures_order(Currency = Currency, order_type = "Long_sell", quantity = Currency.qty_reduce_only, leverage = Currency.leverage)

		time.sleep(1)
		quantity = Binance_trade.define_futures_quantity(Currency = Currency)
		logging.warning(f"{Currency.Currency_crypto}: DEBUG: quantity {quantity} and percentage {percentage}")
		time.sleep(1)

		#place real order
		logging.error(f"{Currency.Currency_crypto}: short buy")
		Binance_trade.do_futures_order(Currency = Currency, order_type = "Short_buy", quantity = quantity, leverage = Currency.leverage)
		Currency.last_qty_order_futures = quantity


if __name__ == "__main__":
   main()
