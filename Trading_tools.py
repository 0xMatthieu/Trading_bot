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
	df['MACD'] = macd['MACD_12_26_9']
	df['Signal'] = macd['MACDs_12_26_9']

	# Determine the buy/sell signal
	signal_value = None
	if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] and df['MACD'].iloc[-2] <= df['Signal'].iloc[-2]:
		signal_value = 'buy'
	elif df['MACD'].iloc[-1] < df['Signal'].iloc[-1] and df['MACD'].iloc[-2] >= df['Signal'].iloc[-2]:
		signal_value = 'sell'

	# Determine the current trend
	trend = 'buy' if df['MACD'].iloc[-1] > df['Signal'].iloc[-1] else 'sell'

	return df, signal_value, trend