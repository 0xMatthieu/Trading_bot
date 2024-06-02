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
	if df[macd_column_name].iloc[-1] > df[signal_column_name].iloc[-1]:
		signal = 'buy'
		trend = 'buy'
	elif df[macd_column_name].iloc[-1] < df[signal_column_name].iloc[-1]:
		signal = 'sell'
		trend = 'sell'

	# Find the most recent crossover point to determine the current trend
	for i in range(len(df) - 1, 0, -1):
		if df[macd_column_name].iloc[i] > df[signal_column_name].iloc[i] and df[macd_column_name].iloc[i - 1] <= df[signal_column_name].iloc[i - 1]:
			trend = 'buy'
			break
		elif df[macd_column_name].iloc[i] < df[signal_column_name].iloc[i] and df[macd_column_name].iloc[i - 1] >= df[signal_column_name].iloc[i - 1]:
			trend = 'sell'
			break

	return df, signal, trend

