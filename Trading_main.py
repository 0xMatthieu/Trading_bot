from Exchange_trade import Exchange
import Sharing_data
from Crypto_definition import Crypto
import pandas as pd
import time
import logging

class FuturesBot(object):

    def __init__(self):
        self.kucoin = Exchange(name='kucoin')

        #crypto
        self.crypto = []
        self.crypto.append(Crypto(symbol_spot='ETH/USDT', symbol_futures='ETHUSDTM', leverage=None, timeframe='1h', percentage = 20, function="FVG"))
        #self.crypto.append(Crypto(symbol_spot='PYTH/USDT', symbol_futures='PYTHUSDTM', leverage=None, timeframe='1h', percentage = 20, function="Order_block"))
        #self.crypto.append(Crypto(symbol_spot='TAO/USDT', symbol_futures='TAOUSDTM', leverage=None, timeframe='1h', percentage = 20, function="Order_block"))
        #self.crypto.append(Crypto(symbol_spot='WIF/USDT', symbol_futures='WIFUSDTM', leverage=None, timeframe='1h', percentage = 20, function="Order_block"))
        #self.crypto.append(Crypto(symbol_spot='ONDO/USDT', symbol_futures='ONDOUSDTM', leverage=None, timeframe='1h', percentage = 20, function="Order_block"))
        self.limit_create = 50

        self.life_data = pd.Timestamp.now()

    def run_futures_trading_function(self, crypto=None, function=None):
        start_time = time.time()
        market_type='futures'
        market_type_spot='spot'
        order_type = 'limit'

        if crypto.df.empty:
            Sharing_data.erase_json_content(filename=crypto.json_file)
            crypto.df = self.kucoin.fetch_klines(symbol=crypto.symbol_spot, timeframe=crypto.timeframe, since=None, limit=self.limit_create, market_type=market_type_spot)
            crypto.update_crypto_dataframe(function=function)
            crypto.df['Quantity'] = 0
            Sharing_data.append_to_file(f"Crypto {crypto.symbol_spot} dataframe created for function {crypto.function}", level=logging.CRITICAL)

        interval = self.kucoin.timeframe_to_int(interval=crypto.timeframe)
        signal_timedelta = self.kucoin.calculate_time_diff_signal(interval=interval, df=crypto.df, ticker_data=None)

        #print(f"Crypto {Crypto.symbol_spot} time execution {time.time() - start_time}")

        if signal_timedelta:
            crypto.df, updated = self.kucoin.fetch_exchange_ticker(symbol=crypto.symbol_spot, df=crypto.df, interval=crypto.timeframe, market_type=market_type_spot)
            if updated:
                crypto.update_crypto_dataframe(function=function, start=1)
                self.kucoin.monitor_and_adjust_stop_orders(symbol=crypto.symbol_futures, stop_loss_long_price=crypto.df['Stop_Loss_Long'].iloc[-1],
                                                           take_profit_long_price=crypto.df['Take_Profit_Long'].iloc[-1], stop_loss_short_price=crypto.df['Stop_Loss_Short'].iloc[-1],
                                                           take_profit_short_price=crypto.df['Take_Profit_Short'].iloc[-1], market_type=market_type)
                Sharing_data.append_to_file(f"DEBUG signal is {crypto.df['Signal'].iloc[-1]}, bull OB is {crypto.df['bullish_OB'].iloc[-1]} and bear OB is {crypto.df['bearish_OB'].iloc[-1]} on {crypto.symbol_spot} at time {crypto.df['timestamp'].max()}", level=logging.CRITICAL)
                if crypto.df['Signal'].iloc[-1]:
                    Sharing_data.append_to_file(f"-----------------------------------------------", level=logging.CRITICAL)
                    Sharing_data.append_to_file(f"signal {crypto.df['Signal'].iloc[-1]} on {crypto.symbol_spot} at time {crypto.df['timestamp'].max()}", level=logging.CRITICAL)
                    if crypto.df['Signal'].iloc[-1] == 'buy' or crypto.df['Signal'].iloc[-1] == 'sell':
                        crypto.df.iloc[-1, crypto.df.columns.get_loc('Quantity')] = self.kucoin.place_order(symbol=crypto.symbol_futures, percentage=crypto.percentage,
                                                                                                            order_side=crypto.df['Signal'].iloc[-1], market_type=market_type, order_type=order_type, leverage=crypto.leverage)
                        self.kucoin.create_stop_orders(symbol=crypto.symbol_futures, signal=crypto.df['Signal'].iloc[-1], stop_loss_long_price=crypto.df['Stop_Loss_Long'].iloc[-1],
                                                       take_profit_long_price=None, stop_loss_short_price=crypto.df['Stop_Loss_Short'].iloc[-1],
                                                       take_profit_short_price=None, market_type=market_type, quantity=crypto.df['Quantity'].iloc[-1])
        return crypto

    def run_main(self, sleep_time=5):
        start_time = time.time()
        for crypto in self.crypto:
            crypto = self.run_futures_trading_function(crypto=crypto, function=crypto.function)
        #print(f"Main crypto algo time execution {time.time() - start_time}")
        self.life_data = Sharing_data.life_data(life_data=self.life_data, level=logging.DEBUG)



if __name__ == "__main__":
    Sharing_data.erase_folder_content(folder_path='data/')
    Sharing_data.append_to_file(f"Function order block", level=logging.CRITICAL)
    Bot = FuturesBot()

    #Bot.run_main()
    
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

