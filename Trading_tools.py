import pandas as pd 
import pandas_ta as ta
import streamlit as st

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

# Function to erase content and start with a fresh new file
def erase_file_data(file_path="data.txt"):
    with open(file_path, 'w') as file:
        # Opening the file in write mode will truncate the file
        pass

# Function to append a string input to a text file if the input is not None
def append_to_file(input_string, file_path="data.txt"):
    if input_string:
        with open(file_path, "a") as file:
            file.write(input_string + "\n")

# Function to read the file and write content using st.write, one line per sentence
def read_and_display_file(file_path="data.txt"):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                st.write(line.strip())
    except FileNotFoundError:
        st.write("File not found. Please add some content first.")