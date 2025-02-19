import pandas as pd
import Trading_tools
import Sharing_data

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

    def update_crypto_dataframe(self, function=None, start=1):
        if function == "Heikin":
            self.df = Trading_tools.calculate_heikin_ashi(self.df)
            self.df = Trading_tools.heikin_ashi_strategy(self.df, start=start, stop_loss=0.01, take_profit=0.02)
        elif function == "Order_block":
            self.df = Trading_tools.calculate_order_blocks(data=self.df, periods=5, threshold=0.0, use_wicks=False, start=1, stop_loss=0.005, take_profit=None)
        elif function == "FVG":
            self.df = Trading_tools.find_fvg(df=self.df)

        Sharing_data.append_to_json(df=self.df, filename=self.json_file)
