import pandas as pd 
import pandas_ta as ta
import numpy as np

def calculate_macd(df, fast=12, slow=26, signal=9, column='close'):
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
	
	for i in range(1, len(df)):
		if df[hist_column_name].iloc[i] > 0 and df[hist_column_name].iloc[i-1] <= 0:
			df.iloc[i, df.columns.get_loc('Signal')] = 'buy'
		elif df[hist_column_name].iloc[i] < 0 and df[hist_column_name].iloc[i-1] >= 0:
			df.iloc[i, df.columns.get_loc('Signal')] = 'sell'

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
	
def heikin_ashi_strategy(df):
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
    
	ha_df['Stop_Loss_Long'] = ha_df['Swing_Low'].shift(1)
	ha_df['Stop_Loss_Short'] = ha_df['Swing_High'].shift(1)
    
	ha_df['Take_Profit_Long'] = 0
	ha_df['Take_Profit_Short'] = 0
	#ha_df['Take_Profit_Long'] = ha_df['HA_Close'] + 2 * (ha_df['HA_Close'] - ha_df['Stop_Loss_Long'])
	#ha_df['Take_Profit_Short'] = ha_df['HA_Close'] - 2 * (ha_df['Stop_Loss_Short'] - ha_df['HA_Close'])
    
	ha_df['Signal'] = None
	ha_df['Trend'] = None
	
    
	for i in range(1, len(ha_df)):
		if ha_df['Down_Count'][i-1] >= 4 and ha_df['HA_Color'][i] == 'green':
			ha_df.iloc[i, ha_df.columns.get_loc('Long_Condition')] = True
			ha_df.iloc[i, ha_df.columns.get_loc('Take_Profit_Long')] = ha_df['HA_Close'][i] + 2 * (ha_df['HA_Close'][i] - ha_df['Stop_Loss_Long'][i])
		if ha_df['Up_Count'][i-1] >= 4 and ha_df['HA_Color'][i] == 'red':
			ha_df.iloc[i, ha_df.columns.get_loc('Short_Condition')] = True
			ha_df.iloc[i, ha_df.columns.get_loc('Take_Profit_Long')] = ha_df['HA_Close'][i] - 2 * (ha_df['Stop_Loss_Short'][i] - ha_df['HA_Close'][i])

		#trend
		if ha_df['Signal'][i] == None:
			ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = ha_df['Trend'][i-1]
		elif ha_df['Signal'][i] == 'buy' or ha_df['Signal'][i] == 'sell':
			ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = ha_df['Signal'][i]

		if ha_df['Trend'][i] == 'buy': 
			if ha_df['HA_Low'][i] <= ha_df['Stop_Loss_Long'][i-1]:
				ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'stop loss long'	# Close long position
				ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
			elif ha_df['HA_Close'][i] >= ha_df['Take_Profit_Long'][i-1]:
				ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'take profit long'	# Close long position
				ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
		elif ha_df['Trend'][i] == 'sell': 
			if ha_df['HA_High'][i] >= ha_df['Stop_Loss_Short'][i-1]:
				ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'stop loss short'	# Close short position
				ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None
			elif ha_df['HA_Close'][i] <= ha_df['Take_Profit_Short'][i-1]:
				ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'take profit short'	# Close short position
				ha_df.iloc[i, ha_df.columns.get_loc('Trend')] = None

		# signal is done at end of function to be sure to not modify signal
		if ha_df['Long_Condition'][i] and not pd.isna(ha_df['Stop_Loss_Long'][i]):
			ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'buy'
		elif ha_df['Short_Condition'][i] and not pd.isna(ha_df['Stop_Loss_Short'][i]):
			ha_df.iloc[i, ha_df.columns.get_loc('Signal')] = 'sell'
    
	return ha_df
