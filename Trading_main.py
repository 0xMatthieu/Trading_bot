from Exchange_trade import Exchange
import Trading_tools
import Sharing_data
import pandas as pd
import time
import logging

class Crypto(object):
    def __init__(self, symbol_spot=None, symbol_futures=None, leverage = None, timeframe = '1m', percentage = 20, function="MACD"):
        self.symbol_spot = symbol_spot
        self.symbol_futures = symbol_futures
        self.df = pd.DataFrame()
        self.leverage = leverage
        self.timeframe = timeframe
        self.percentage = percentage
        # data sharing
        self.folder_path = 'data/'
        self.json_file = self.folder_path + symbol_spot.replace('/', '_') + '.json'
        self.function = function


class Futures_bot(object):

    def __init__(self):
        self.kucoin = Exchange(name='kucoin')
        self.kucoin.load_market(market_type='spot')
        self.kucoin.load_market(market_type='futures')

        #crypto
        self.crypto = []
        self.crypto.append(Crypto(symbol_spot='ETH/USDT', symbol_futures='ETHUSDTM', leverage=None, timeframe='5m', percentage = 20, function="Order_block"))
        self.crypto.append(Crypto(symbol_spot='PYTH/USDT', symbol_futures='PYTHUSDTM', leverage=None, timeframe='5m', percentage = 20, function="Order_block"))
        self.crypto.append(Crypto(symbol_spot='TAO/USDT', symbol_futures='TAOUSDTM', leverage=None, timeframe='5m', percentage = 20, function="Order_block"))
        self.crypto.append(Crypto(symbol_spot='WIF/USDT', symbol_futures='WIFUSDTM', leverage=None, timeframe='5m', percentage = 20, function="Order_block"))
        self.crypto.append(Crypto(symbol_spot='ONDO/USDT', symbol_futures='ONDOUSDTM', leverage=None, timeframe='5m', percentage = 20, function="Order_block"))

        self.macd_fast = 180 #standart 12, binance 180
        self.macd_slow = 390 #standart 26, binance 390
        self.macd_signal = 135 #standart 9, binance 135
        self.limit_create = 50

        self.life_data = pd.Timestamp.now()

    def update_crypto_dataframe(self, Crypto=None, function=None, start=1):
        if function == "MACD":
            Crypto.df = Trading_tools.calculate_macd(Crypto.df, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal, column='close', start=start, stop_loss = 0.02, take_profit = 0.02)
        elif function == "MACD_Heikin":
            Crypto.df = Trading_tools.calculate_heikin_ashi(Crypto.df)
            Crypto.df = Trading_tools.calculate_macd(Crypto.df, fast=self.macd_fast, slow=self.macd_slow, signal=self.macd_signal, column='HA_Close', start=start, stop_loss = 0.02, take_profit = 0.02)
        elif function == "Heikin":
            Crypto.df = Trading_tools.calculate_heikin_ashi(Crypto.df)
            Crypto.df = Trading_tools.heikin_ashi_strategy(Crypto.df, start=start, stop_loss = 0.01, take_profit = 0.02)
        elif function == "Order_block":
            Crypto.df = Trading_tools.calculate_order_blocks(data=Crypto.df, periods=5, threshold=0.0, use_wicks=False, start=1, stop_loss = 0.005, take_profit = None)
        
        Sharing_data.append_to_json(df=Crypto.df, filename=Crypto.json_file)
        return Crypto

    def run_futures_trading_function(self, Crypto=None, function=None):
        start_time = time.time()
        market_type='futures'
        market_type_spot='spot'
        order_type = 'limit'

        if Crypto.df.empty:
            Sharing_data.erase_json_content(filename=Crypto.json_file)
            Crypto.df = self.kucoin.fetch_klines(symbol=Crypto.symbol_spot, timeframe=Crypto.timeframe, since=None, limit=self.limit_create, market_type=market_type_spot)
            Crypto = self.update_crypto_dataframe(Crypto=Crypto, function=function)
            Crypto.df['Quantity'] = 0
            Sharing_data.append_to_file(f"Crypto {Crypto.symbol_spot} dataframe created for function {Crypto.function}", level=logging.CRITICAL)

        interval = self.kucoin.timeframe_to_int(interval=Crypto.timeframe)
        signal_timedelta = self.kucoin.calculate_time_diff_signal(interval=interval, df=Crypto.df, ticker_data=None)

        #print(f"Crypto {Crypto.symbol_spot} time execution {time.time() - start_time}")

        if signal_timedelta:
            Crypto.df, updated = self.kucoin.fetch_exchange_ticker(symbol=Crypto.symbol_spot, df=Crypto.df, interval=Crypto.timeframe, market_type=market_type_spot)
            if updated:
                Crypto = self.update_crypto_dataframe(Crypto=Crypto, function=function, start=1)
                self.kucoin.monitor_and_adjust_stop_orders(symbol=Crypto.symbol_futures, stop_loss_long_price=Crypto.df['Stop_Loss_Long'].iloc[-1], 
                    take_profit_long_price=Crypto.df['Take_Profit_Long'].iloc[-1], stop_loss_short_price=Crypto.df['Stop_Loss_Short'].iloc[-1], 
                    take_profit_short_price=Crypto.df['Take_Profit_Short'].iloc[-1],  market_type=market_type)
                Sharing_data.append_to_file(f"DEBUG signal is {Crypto.df['Signal'].iloc[-1]}, bull OB is {Crypto.df['bullish_OB'].iloc[-1]} and bear OB is {Crypto.df['bearish_OB'].iloc[-1]} on {Crypto.symbol_spot} at time {Crypto.df['timestamp'].max()}", level=logging.CRITICAL)
                if Crypto.df['Signal'].iloc[-1]:
                    Sharing_data.append_to_file(f"-----------------------------------------------", level=logging.CRITICAL)
                    Sharing_data.append_to_file(f"signal {Crypto.df['Signal'].iloc[-1]} on {Crypto.symbol_spot} at time {Crypto.df['timestamp'].max()}", level=logging.CRITICAL)
                    if Crypto.df['Signal'].iloc[-1] == 'buy' or Crypto.df['Signal'].iloc[-1] == 'sell':
                        Crypto.df.iloc[-1, Crypto.df.columns.get_loc('Quantity')] = self.kucoin.place_order(symbol=Crypto.symbol_futures, percentage=Crypto.percentage, 
                            order_side=Crypto.df['Signal'].iloc[-1], market_type=market_type, order_type=order_type, leverage=Crypto.leverage)
                        self.kucoin.create_stop_orders(symbol=Crypto.symbol_futures, signal=Crypto.df['Signal'].iloc[-1], stop_loss_long_price=Crypto.df['Stop_Loss_Long'].iloc[-1], 
                            take_profit_long_price=None, stop_loss_short_price=Crypto.df['Stop_Loss_Short'].iloc[-1], 
                            take_profit_short_price=None,  market_type=market_type, quantity=Crypto.df['Quantity'].iloc[-1])
        return Crypto

    def run_main(self, sleep_time=5):
        start_time = time.time()
        for crypto in self.crypto:
            crypto = self.run_futures_trading_function(Crypto=crypto, function=crypto.function)
        #print(f"Main crypto algo time execution {time.time() - start_time}")
        self.life_data = Sharing_data.life_data(life_data=self.life_data, level=logging.DEBUG)



if __name__ == "__main__":
    Bot = Futures_bot()
    Sharing_data.erase_folder_content(folder_path=Bot.crypto[0].folder_path)
    Sharing_data.append_to_file(f"Function order block", level=logging.CRITICAL)
    while True:
        Bot.run_main()
    
    #Bot.crypto[0].df
    #Bot.crypto[0]=Bot.update_crypto_dataframe(Crypto=Bot.crypto[0], function="Order_block", start=1)
    #Bot.crypto[0].df, updated = Bot.kucoin.fetch_exchange_ticker(symbol=Bot.crypto[0].symbol_spot, df=Bot.crypto[0].df, interval=Bot.crypto[0].timeframe, market_type='spot')
    #Bot.crypto[0].df
    #new_df = Bot.kucoin.fetch_klines(symbol=Bot.crypto[0].symbol_spot, timeframe=Bot.crypto[0].timeframe, since=None, limit=2, market_type='spot')
    #df = pd.concat([Bot.crypto[0].df, new_df], ignore_index=True)
    #df.drop(df.tail(2).index,inplace=True)
    #df = pd.concat([Bot.crypto[0].df, new_df], ignore_index=True)
    #Bot.kucoin.fetch_balance(currency='USDT', account='free', market_type='futures')
    #Bot.kucoin.fetch_market_data(symbol='ETHUSDTM', market_type='futures')
    #Bot.kucoin.fetch_exchange_ticker(symbol='ETHUSDTM', interval='1m', market_type='futures')
    #Bot.kucoin.fetch_klines(symbol='ETHUSDTM', limit=200, market_type='futures')
    #Bot.kucoin.place_market_order(symbol='ETH/USDT', percentage=50, order_type='buy', market_type='spot')
    #Bot.kucoin.place_market_order(symbol='ETHUSDTM', percentage=25, order_type='buy', market_type='futures', leverage=None, reduceOnly=False)

