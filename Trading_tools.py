import pandas as pd 
import pandas_ta as ta

def calculate_macd(df, fast=12, slow=26, signal=9):
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
	macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    
	macd_column_name = f'MACD'			#f'MACD_{fast}_{slow}_{signal}'
	signal_column_name = f'MACDs'		#f'MACDs_{fast}_{slow}_{signal}'
	hist_column_name = f'MACDh'		#f'MACDh_{fast}_{slow}_{signal}'
    
	df[macd_column_name] = macd[f'MACD_{fast}_{slow}_{signal}']
	df[signal_column_name] = macd[f'MACDs_{fast}_{slow}_{signal}']
	df[hist_column_name] = macd[f'MACDh_{fast}_{slow}_{signal}']

	# Determine buy/sell signals
	signal = None
	trend = None

	if df[macd_column_name].iloc[0] > df[signal_column_name].iloc[0] and df[macd_column_name].iloc[-1] <= df[signal_column_name].iloc[-1]:
		signal_value = 'buy'
	elif df[macd_column_name].iloc[0] < df[signal_column_name].iloc[0] and df[macd_column_name].iloc[-1] >= df[signal_column_name].iloc[-1]:
		signal_value = 'sell'

	# Determine the current trend
	trend = 'buy' if df[macd_column_name].iloc[0] > df[signal_column_name].iloc[0] else 'sell'

	return df, signal, trend

def calculate_heikin_ashi(df):
	ha_df = df.copy()
	ha_df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    
	ha_open = [df['Open'][0]]
	for i in range(1, len(df)):
		ha_open.append((ha_open[-1] + ha_df['HA_Close'][i-1]) / 2)
	ha_df['HA_Open'] = ha_open
    
	ha_df['HA_High'] = ha_df[['HA_Open', 'HA_Close', 'High']].max(axis=1)
	ha_df['HA_Low'] = ha_df[['HA_Open', 'HA_Close', 'Low']].min(axis=1)
    
	ha_df['HA_Color'] = np.where(ha_df['HA_Close'] >= ha_df['HA_Open'], 'green', 'red')
    
	ha_df['Up_Count'] = (ha_df['HA_Color'] == 'green').astype(int).groupby((ha_df['HA_Color'] != 'green').cumsum()).cumsum()
	ha_df['Down_Count'] = (ha_df['HA_Color'] == 'red').astype(int).groupby((ha_df['HA_Color'] != 'red').cumsum()).cumsum()
    
	ha_df['Swing_High'] = ha_df['HA_High'].rolling(window=5, center=False).max()
	ha_df['Swing_Low'] = ha_df['HA_Low'].rolling(window=5, center=False).min()
    
	ha_df['Long_Condition'] = (ha_df['Down_Count'] >= 4) & (ha_df['HA_Color'] == 'green')
	ha_df['Short_Condition'] = (ha_df['Up_Count'] >= 4) & (ha_df['HA_Color'] == 'red')
    
	ha_df['Stop_Loss_Long'] = ha_df['Swing_Low'].shift(1)
	ha_df['Stop_Loss_Short'] = ha_df['Swing_High'].shift(1)
    
	ha_df['Take_Profit_Long'] = ha_df['HA_Close'] + 2 * (ha_df['HA_Close'] - ha_df['Stop_Loss_Long'])
	ha_df['Take_Profit_Short'] = ha_df['HA_Close'] - 2 * (ha_df['Stop_Loss_Short'] - ha_df['HA_Close'])
    
	ha_df['Signal'] = np.nan
    
	for i in range(1, len(ha_df)):
		if ha_df['Long_Condition'][i] and not pd.isna(ha_df['Stop_Loss_Long'][i]):
			ha_df['Signal'][i] = 'buy'
		elif ha_df['Short_Condition'][i] and not pd.isna(ha_df['Stop_Loss_Short'][i]):
			ha_df['Signal'][i] = 'sell'
		elif ha_df['Signal'][i-1] == 'buy' and (ha_df['HA_Low'][i] <= ha_df['Stop_Loss_Long'][i-1] or ha_df['HA_Close'][i] >= ha_df['Take_Profit_Long'][i-1]):
			ha_df['Signal'][i] = 'sell'  # Close long position
		elif ha_df['Signal'][i-1] == 'sell' and (ha_df['HA_High'][i] >= ha_df['Stop_Loss_Short'][i-1] or ha_df['HA_Close'][i] <= ha_df['Take_Profit_Short'][i-1]):
			ha_df['Signal'][i] = 'buy'  # Close short position

	signal = ha_df['Signal'].iloc[0]
    
	return ha_df, signal
