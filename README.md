# Trading_bot

A simple bot using ccxt library to trade on centralized exchanges (CEX) such as Binance and KuCoin.
The aim is to test different trading strategies automatically.

## Project Structure

- Exchange_trade.py: Contains the Exchange class interacting with CEX APIs.
- Sharing_data.py: Provides data sharing utilities such as logging and file management.
- Trading_main.py: Implements the core trading logic and strategy evaluation.
- Trading_tools.py: Offers helper functions for technical analysis and trading strategies.
- streamlit_app.py: A Streamlit-based web dashboard for visualizing trading performance.
- webhook_receiver.py: Handles incoming webhook requests for auto-updates.

## Additional Files

- .gitignore: Specifies files and directories to be ignored by git.
- LICENSE: Contains the licensing information.
- README.md: This file.
- requirements.txt: Lists the project's dependencies.

## Getting Started

1. Install dependencies:
   pip install -r requirements.txt

2. Run the main trading script:
   python Trading_main.py

3. Start the Streamlit app:
   streamlit run streamlit_app.py

