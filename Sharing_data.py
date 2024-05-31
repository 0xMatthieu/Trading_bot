import pandas as pd 
import streamlit as st
import json

# Function to erase content and start with a fresh new file
def erase_file_data(file_path="data/data.txt"):
    with open(file_path, 'w') as file:
        # Opening the file in write mode will truncate the file
        pass

# Function to append a string input to a text file if the input is not None
def append_to_file(input_string, file_path="data/data.txt"):
    if input_string:
        with open(file_path, "a") as file:
            file.write(input_string + "\n")

# Function to read the file and write content using st.write, one line per sentence
def read_and_display_file(file_path="data/data.txt"):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                st.write(line.strip())
    except FileNotFoundError:
        st.write("File not found. Please add some content first.")

# Function to erase JSON content
def erase_json_content(filename):
	# Write an empty list to the JSON file
	with open(filename, 'w') as f:
		json.dump([], f)

# Function to append DataFrame to JSON
def append_to_json(df, filename):
	# Convert DataFrame to list of dictionaries with Timestamps as strings
	records = df.to_dict(orient='records')
	for record in records:
		for key, value in record.items():
			if isinstance(value, pd.Timestamp):
				record[key] = value.isoformat()

	# Load existing data
	try:
		with open(filename, 'r') as f:
			data = json.load(f)
	except FileNotFoundError:
		data = []

	# Append new records
	data.extend(records)

	# Write updated data back to the file
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)


def read_json(filename):
	try:
		with open(filename, 'r') as f:
			data = json.load(f)
	except FileNotFoundError:
		data = []

	# Convert timestamp strings back to Timestamps
	for record in data:
		for key, value in record.items():
			if isinstance(value, str):
				try:
					# Attempt to convert string to Timestamp
					record[key] = pd.Timestamp(value)
				except ValueError:
					# If conversion fails, keep the original value
					pass

	return pd.DataFrame(data)
