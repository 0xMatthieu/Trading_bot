
import os
import pandas as pd 
from binance.exceptions import BinanceAPIException, BinanceOrderException
from binance import ThreadedWebsocketManager, Client
import numpy as np
from dotenv import load_dotenv

class Currency:
    "currency class"

    def __init__(self, Currency, Currency_crypto):
        self.Currency = Currency
        self.Currency_crypto = Currency_crypto
        self.price = {Currency: pd.DataFrame(columns=['date', 'price']), 'error':False, 'old_price':0, 'price_stuck':0, 'price_stuck_algo':0, 'old_price_algo':0}
        self.current_crypto_available = 0
        self.current_price = 0
        self.last_price = 0
        self.historical = 0
        self.historical_supertrend = 0
        self.min_notional = 0
        self.precision = 0
        self.twm = 0 # init in binance trade ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
        self.percentage = 1
        #third algo
        self.df_macd = 0
        self.df_macd_last_value = 0
        self.df_macd_240 = 0
        self.df_macd_last_value_240 = 0
        self.df_macd_60 = 0
        self.df_macd_last_value_60 = 0
        self.df_macd_30 = 0
        self.df_macd_last_value_30 = 0
        self.macd_status = 'None'
        self.macd_trend = 'None'
        self.delta = 0
        self.old_delta = 0
        self.max_value = 0

        self.buy_good_trade = 0
        self.buy_bad_trade = 0
        self.sell_good_trade = 0
        self.sell_bad_trade = 0
        self.benefit_buy = 1
        self.benefit_sell = 1
        self.price_start_trade = 0
        self.price_out_trade = 0
        self.init = True

        self.futures_long_price = 0
        self.futures_short_price = 0
        self.current_future = 'None'
        self.leverage = 4

        self.ema_trend = 'None'


        #test 
        self.historical_price = 0



def init():
    global Currency_fiat, twm, client, do_real_order, \
    total_money_available, current_money_available, level_to_buy_array, current_total, balance, order_done_current_cycle, \
    level_to_sell_array, percentage_to_sell_array, \
    percentage_to_buy_array, api_key, api_secret, test, \
    total_money_available_futures, current_money_available_futures, balance_futures, asset_futures

    #general
    do_real_order = False
    test = False
    Currency_fiat = 'EUR'
    total_money_available = 0
    total_money_available_futures = 0
    current_money_available = 0
    current_money_available_futures = 0
    current_total = 0
    asset_futures = 0
    balance = 0
    balance_futures = 0
    order_done_current_cycle = False
    #second algo
    percentage_to_buy_array = np.array([0.1, 0.1, 0.2, 0.3, 0.5, 0.6, 0.1, 0.1, 0.2, 0.3, 0.5, 0.6])
    level_to_buy_array = np.array([0.98, 0.96, 0.95, 0.90, 0.85, 0.8, 1, 1.01, 1.01, 1.03, 1.05, 1.05])
    level_to_sell_array = np.array([1, 0.98, 0.98, 0.95, 0.95, 0.9, 1.02, 1.04, 1.06, 1.08, 1.1, 1.2])
    percentage_to_sell_array = np.array([0.1, 0.1, 0.1, 0.3, 0.5, 0.5, 0.1, 0.1, 0.1, 0.3, 0.5, 0.5])
    #third algo

    # init
    load_dotenv(dotenv_path=".env")
    api_key = os.environ.get('api_key_binance')
    api_secret = os.environ.get('api_secret_binance')
    client = Client(api_key, api_secret)


