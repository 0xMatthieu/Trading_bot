from Crypto_definition import Crypto
import os
import pandas as pd

def evaluate_strategy_performance(df, start=1):
    initial_balance = 10000  # Starting balance for the simulation
    balance = initial_balance
    position = None
    entry_price = 0
    pnl = 0

    # Calculate buy and hold PnL
    buy_and_hold_entry = df['close'].iloc[start]
    buy_and_hold_exit = df['close'].iloc[-1]
    buy_and_hold_pnl = (buy_and_hold_exit - buy_and_hold_entry) * 100 / buy_and_hold_entry

    for i in range(start, len(df)):
        if df['Signal'].iloc[i] == 'buy' and position is None:
            # Enter a long position
            position = 'long'
            entry_price = df['close'].iloc[i]
            print(f"Entering long at {entry_price}")

        elif df['Signal'].iloc[i] == 'sell' and position is None:
            # Enter a short position
            position = 'short'
            entry_price = df['close'].iloc[i]
            print(f"Entering short at {entry_price}")

        elif position == 'long' and (df['Signal'].iloc[i] == 'sell' or df['close'].iloc[i] <= df['Stop_Loss_Long'].iloc[i]):
            # Exit long position
            exit_price = df['close'].iloc[i]
            trade_pnl = (exit_price - entry_price) * 100 / entry_price
            pnl += trade_pnl
            balance += balance * trade_pnl / 100
            print(f"Exiting long at {exit_price}, PnL: {trade_pnl}%")
            position = None

        elif position == 'short' and (df['Signal'].iloc[i] == 'buy' or df['close'].iloc[i] >= df['Stop_Loss_Short'].iloc[i]):
            # Exit short position
            exit_price = df['close'].iloc[i]
            trade_pnl = (entry_price - exit_price) * 100 / entry_price
            pnl += trade_pnl
            balance += balance * trade_pnl / 100
            print(f"Exiting short at {exit_price}, PnL: {trade_pnl}%")
            position = None

    return {
        "total_pnl": pnl,
        "final_balance": balance,
        "return_percentage": (balance - initial_balance) * 100 / initial_balance,
        "buy_and_hold_pnl": buy_and_hold_pnl
    }

def fetch_and_store_historical_data(exchange=None, symbol='BTC/USDT', timeframe='1h', limit=1000, market_type='spot', erase=False):
    file_path = f"data/{symbol.replace('/', '_')}_{timeframe}.json"
    if not os.path.exists(file_path) or erase is True:
        df = exchange.fetch_klines(symbol=symbol, timeframe=timeframe, since=None, limit=limit, market_type=market_type)
        df.to_json(file_path, orient='records', date_format='iso')
    else:
        df = pd.read_json(file_path, orient='records', convert_dates=False)
    return df

def backtest_strategy(self, exchange=None, symbol='BTC/USDT', timeframes=None, function="FVG"):
    if timeframes is None:
        timeframes = ['1h', '4h', '1d']
    results = {}
    for timeframe in timeframes:
        df = self.fetch_and_store_historical_data(exchange=exchange, symbol=symbol, timeframe=timeframe)
        crypto = Crypto(symbol_spot=symbol, symbol_futures=symbol.replace('/', '') + 'M', timeframe=timeframe, function=function)
        crypto.df = df
        crypto.update_crypto_dataframe(function=function)
        results[timeframe] = evaluate_strategy_performance(crypto.df)
    return results
