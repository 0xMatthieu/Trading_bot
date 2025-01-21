import pandas as pd 
import pandas_ta as ta
import numpy as np

def round_down(value, decimals):
    #https://stackoverflow.com/questions/41383787/round-down-to-2-decimal-in-python
    factor = 1 / (10 ** decimals)
    return (value // factor) * factor

def calculate_stop_loss_at_signal(df, i, column, stop_loss):
    if df['Signal'][i] == 'buy':
        df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df[column][i] * (1-stop_loss)
    elif df['Signal'][i] == 'sell':
        df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df[column][i] * (1+stop_loss)
    return df

def update_stop_loss_trailing_stop(df, i, column, stop_loss):
    df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df['Stop_Loss_Long'][i-1]
    df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df['Stop_Loss_Short'][i-1]

    if df['Trend'][i] == 'buy' and i < len(df)-1:	# needed cause last candle is retrieved with incomplete value
        if df[column][i] > df[column][i-1]:	# if price increased as expected in buy trend
            if df['Stop_Loss_Long'][i-1] is not None and df['Stop_Loss_Long'][i-1] < df[column][i] * (1-stop_loss):	# stop loss can only increase, not decrease
                df.iloc[i, df.columns.get_loc('Stop_Loss_Long')] = df[column][i] * (1-stop_loss)
    elif df['Trend'][i] == 'sell' and i < len(df)-1:	# needed cause last candle is retrieved with incomplete value
        if df[column][i] < df[column][i-1]:
            if df['Stop_Loss_Short'][i-1] is not None and df['Stop_Loss_Short'][i-1] > df[column][i] * (1+stop_loss):
                df.iloc[i, df.columns.get_loc('Stop_Loss_Short')] = df[column][i] * (1+stop_loss)

    return df

def calculate_macd(df, fast=12, slow=26, signal=9, column='close', start=1, stop_loss = 0.01, take_profit = 0.02):

    """
    Calculate MACD and determine buy/sell signals.

    Parameters:
    - df: DataFrame with OHLCV data, including 'close' column.
    - fast: Fast EMA period (default is 12).
    - slow: Slow EMA period (default is 26).
    - signal: Signal line EMA period (default is 9).

    Returns:
    - Updated DataFrame with MACD and Signal columns.
    - Signal ('buy', 'sell', or None).
    - Current trend ('buy' or 'sell').
    """
    # Ensure the DataFrame has enough data to calculate MACD
    min_periods = slow + signal
    if len(df) < min_periods:
        print(f"Not enough data to calculate MACD. Need at least {min_periods} periods.")
        return df, None, None

    # Calculate MACD
    macd = ta.macd(df[column], fast=fast, slow=slow, signal=signal)
    
    macd_column_name = f'MACD'			#f'MACD_{fast}_{slow}_{signal}'
    signal_column_name = f'MACDs'		#f'MACDs_{fast}_{slow}_{signal}'
    hist_column_name = f'MACDh'		#f'MACDh_{fast}_{slow}_{signal}'
    
    df[macd_column_name] = macd[f'MACD_{fast}_{slow}_{signal}']
    df[signal_column_name] = macd[f'MACDs_{fast}_{slow}_{signal}']
    df[hist_column_name] = macd[f'MACDh_{fast}_{slow}_{signal}']

    df['Signal'] = None
    df['Trend'] = None
    df['Stop_Loss_Long'] = None
    df['Stop_Loss_Short'] = None
    df['Take_Profit_Long'] = None # no take profit, act as trailing stop 	df[column] * (1+take_profit)
    df['Take_Profit_Short'] = None # no take profit, act as trailing stop 	df[column] * (1-take_profit)
    
    for i in range(start, len(df)):
        if df[hist_column_name].iloc[i] > 0 and df[hist_column_name].iloc[i-1] <= 0:
            df.iloc[i, df.columns.get_loc('Signal')] = 'buy'
        elif df[hist_column_name].iloc[i] < 0 and df[hist_column_name].iloc[i-1] >= 0:
            df.iloc[i, df.columns.get_loc('Signal')] = 'sell'

        #trend
        if df['Signal'][i] == 'buy' or df['Signal'][i] == 'sell':
            df.iloc[i, df.columns.get_loc('Trend')] = df['Signal'][i]
        elif df['Signal'][i] == None:
            df.iloc[i, df.columns.get_loc('Trend')] = df['Trend'][i-1]

        # stop loss
        df = update_stop_loss_trailing_stop(df=df, i=i, column=column, stop_loss=stop_loss)
        df = calculate_stop_loss_at_signal(df=df, i=i, column=column, stop_loss=stop_loss)
        

    # Determine the current trend
    #trend = 'buy' if df[macd_column_name].iloc[0] > df[signal_column_name].iloc[0] else 'sell'

    return df
    
def calculate_heikin_ashi(df):
    ha_df = df.copy()
    ha_df['HA_Close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    ha_open = [df['open'][0]]
    for i in range(1, len(df)):
        ha_open.append((ha_open[-1] + ha_df['HA_Close'][i-1]) / 2)
    ha_df['HA_Open'] = ha_open
    
    ha_df['HA_High'] = ha_df[['HA_Open', 'HA_Close', 'high']].max(axis=1)
    ha_df['HA_Low'] = ha_df[['HA_Open', 'HA_Close', 'low']].min(axis=1)
    
    return ha_df
    
def heikin_ashi_strategy(df, start=1, stop_loss = 0.01, take_profit = 0.02):
    #need Heilin Ashi df as input
    ha_df = df.copy()
    ha_df['HA_Color'] = np.where(ha_df['HA_Close'] >= ha_df['HA_Open'], 'green', 'red')
    
    ha_df['Up_Count'] = (ha_df['HA_Color'] == 'green').astype(int).groupby((ha_df['HA_Color'] != 'green').cumsum()).cumsum()
    ha_df['Down_Count'] = (ha_df['HA_Color'] == 'red').astype(int).groupby((ha_df['HA_Color'] != 'red').cumsum()).cumsum()

    ha_df['Long_Condition'] = False
    ha_df['Short_Condition'] = False

    # Debugging: Print to ensure correct calculation
    #print(ha_df.tail(20))
    
    ha_df['Swing_High'] = ha_df['HA_High'].rolling(window=5, center=False).max()
    ha_df['Swing_Low'] = ha_df['HA_Low'].rolling(window=5, center=False).min()
    
    ha_df['Stop_Loss_Long'] = None # no take profit, act as trailing stop ha_df['Swing_Low'].shift(1)
    ha_df['Stop_Loss_Short'] = None # no take profit, act as trailing stop ha_df['Swing_High'].shift(1)
    
    ha_df['Take_Profit_Long'] = ha_df['Swing_High'] + 2 * (ha_df['Swing_High'] - ha_df['Stop_Loss_Long'])
    ha_df['Take_Profit_Short'] = ha_df['Swing_Low'] - 2 * (ha_df['Stop_Loss_Short'] - ha_df['Swing_Low'])
    
    ha_df['Signal'] = None
    ha_df['Trend'] = None
    
    
    for i in range(start, len(ha_df)):	# -1 needed cause klines function returns the last candle which just started and is not complete. this candle cannot be taken
        if ha_df['Down_Count'][i-1] >= 4 and ha_df['HA_Color'][i] == 'green':
            ha_df.iloc[i, ha_df.columns.get_loc('Long_Condition')] = True
        if ha_df['Up_Count'][i-1] >= 4 and ha_df['HA_Color'][i] == 'red':
            ha_df.iloc[i, ha_df.columns.get_loc('Short_Condition')] = True

        #trend
        if ha_df['Signal'][i] == 'buy' or ha_df['Signal'][i] == 'sell':
            ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = ha_df['Signal'][i]
        elif ha_df['Signal'][i] == None:
            ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = ha_df['Trend'][i-1]

        """
        if ha_df['Trend'][i] == 'buy': 
            if ha_df['HA_Low'][i] <= ha_df['Stop_Loss_Long'][i-1]:
                ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'stop_loss_long'	# Close long position
                ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
            elif ha_df['HA_Close'][i] >= ha_df['Take_Profit_Long'][i-1]:
                ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'take_profit_long'	# Close long position
                ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
        elif ha_df['Trend'][i] == 'sell': 
            if ha_df['HA_High'][i] >= ha_df['Stop_Loss_Short'][i-1]:
                ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'stop_loss_short'	# Close short position
                ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
            elif ha_df['HA_Close'][i] <= ha_df['Take_Profit_Short'][i-1]:
                ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'take_profit_short'	# Close short position
                ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
        """
        # signal is done at end of function to be sure to not modify signal
        if ha_df['Long_Condition'][i]:
            ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'buy'
        elif ha_df['Short_Condition'][i]:
            ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'sell'

        # stop loss
        ha_df = update_stop_loss_trailing_stop(df=ha_df, i=i, column='HA_Close', stop_loss=stop_loss)
        ha_df = calculate_stop_loss_at_signal(df=ha_df, i=i, column='HA_Close', stop_loss=stop_loss)
    
    return ha_df

# Function to calculate bullish and bearish order blocks
def calculate_order_blocks(data, periods=5, threshold=0.0, use_wicks=False, start=1, stop_loss = 0.01, take_profit = 0.02):
    ob_period = periods + 1
    data["abs_move"] = (
        abs(data["close"].shift(-ob_period) - data["close"]) / data["close"] * 100
    )
    data["rel_move"] = data["abs_move"] >= threshold
    
    # Bullish OB Identification
    data["bullish_OB"] = False
    for i in range(len(data) - periods - 1):
        if (
            data["close"].iloc[i] < data["open"].iloc[i]  # Red candle
            and all(data["close"].iloc[i + j + 1] > data["open"].iloc[i + j + 1] for j in range(periods))  # Subsequent green candles
            and data["rel_move"].iloc[i]
        ):
            data.loc[i, "bullish_OB"] = True
    
    # Bearish OB Identification
    data["bearish_OB"] = False
    for i in range(len(data) - periods - 1):
        if (
            data["close"].iloc[i] > data["open"].iloc[i]  # Green candle
            and all(data["close"].iloc[i + j + 1] < data["open"].iloc[i + j + 1] for j in range(periods))  # Subsequent red candles
            and data["rel_move"].iloc[i]
        ):
            data.loc[i, "bearish_OB"] = True
    
    data['Signal'] = None
    data['Trend'] = None
    data['Stop_Loss_Long'] = None
    data['Stop_Loss_Short'] = None
    data['Take_Profit_Long'] = None # no take profit, act as trailing stop 	df[column] * (1+take_profit)
    data['Take_Profit_Short'] = None # no take profit, act as trailing stop 	df[column] * (1-take_profit)
    
    for i in range(start, len(data) - 1): # -1 needed cause klines function returns the last candle which just started and is not complete. this candle cannot be taken 
        if data["bullish_OB"].iloc[i] == True:
            data.iloc[i + 1, data.columns.get_loc('Signal')] = 'buy'  # add +1 to index, needed to wait confirmation and trigger order asap
        elif data["bearish_OB"].iloc[i] == True:
            data.iloc[i + 1, data.columns.get_loc('Signal')] = 'sell'   # add +1 to index, needed to wait confirmation and trigger order asap

        #trend
        if data['Signal'][i] == 'buy' or data['Signal'][i] == 'sell':
            data.iloc[i, data.columns.get_loc('Trend')] = data['Signal'][i]
        elif data['Signal'][i] == None:
            data.iloc[i, data.columns.get_loc('Trend')] = data['Trend'][i-1]

    # stop loss
    data = update_stop_loss_trailing_stop(df=data, i=i, column="close", stop_loss=stop_loss)
    data = calculate_stop_loss_at_signal(df=data, i=i, column="close", stop_loss=stop_loss)

    return data

def find_fvg(df, start=1, stop_loss_percent=0.01):
    """
    Identify Fair Value Gaps (FVGs) and generate trading signals.
    FVG is defined as a 3-candle pattern where:
    - Bullish FVG: High of first candle < Low of third candle
    - Bearish FVG: Low of first candle > High of third candle
    
    Signals are placed at 50% of FVG range with stop loss below/above the FVG.
    """
    df = df.copy()
    
    # Initialize columns
    df['FVG_Bullish'] = False
    df['FVG_Bearish'] = False
    df['Signal'] = None
    df['Trend'] = None
    df['Stop_Loss_Long'] = None
    df['Stop_Loss_Short'] = None
    df['Take_Profit_Long'] = None
    df['Take_Profit_Short'] = None
    
    for i in range(start, len(df)):
        # Check for Bullish FVG (current candle is third in pattern)
        if i >= 2:
            prev2_high = df['high'].iloc[i-2]
            prev1_low = df['low'].iloc[i-1]
            current_low = df['low'].iloc[i]
            
            # Bullish FVG condition
            if prev2_high < current_low:
                df.loc[i, 'FVG_Bullish'] = True
                # Calculate 50% entry point and stop loss
                fvg_low = min(df['low'].iloc[i-2], df['low'].iloc[i-1])
                entry_price = (fvg_low + df['high'].iloc[i]) / 2
                df.loc[i, 'Signal'] = 'buy'
                df.loc[i, 'Stop_Loss_Long'] = fvg_low * (1 - stop_loss_percent)
                
        # Check for Bearish FVG (current candle is third in pattern)
        if i >= 2:
            prev2_low = df['low'].iloc[i-2]
            prev1_high = df['high'].iloc[i-1]
            current_high = df['high'].iloc[i]
            
            # Bearish FVG condition
            if prev2_low > current_high:
                df.loc[i, 'FVG_Bearish'] = True
                # Calculate 50% entry point and stop loss
                fvg_high = max(df['high'].iloc[i-2], df['high'].iloc[i-1])
                entry_price = (fvg_high + df['low'].iloc[i]) / 2
                df.loc[i, 'Signal'] = 'sell'
                df.loc[i, 'Stop_Loss_Short'] = fvg_high * (1 + stop_loss_percent)
        
        # Update trend
        if df['Signal'].iloc[i] in ['buy', 'sell']:
            df.loc[i, 'Trend'] = df['Signal'].iloc[i]
        else:
            df.loc[i, 'Trend'] = df['Trend'].iloc[i-1] if i > 0 else None

    return df
