# Trading_bot

A simple bot using ccxt library to trade on centralized exchanges (CEX) such as Binance and KuCoin. The aim is to test different trading strategies automatically.

## Project Structure

- Exchange_trade.py: Contains the Exchange class and helper functions to connect and interact with CEX APIs via ccxt. This module handles market data, trading orders, and risk management.
- Sharing_data.py: Provides utilities for logging, file operations, and JSON handling to share data between modules.
- Trading_main.py: Implements the main trading logic, including backtesting and live trading process orchestration.
- Trading_tools.py: Offers various technical analysis tools, such as MACD, Heikin Ashi calculations, order block identification, and Fair Value Gap (FVG) detection.
- streamlit_app.py: A web dashboard built with Streamlit for visualizing trading performance, data analytics, and real-time monitoring.
- webhook_receiver.py: A Flask-based webhook handler to automatically deploy code updates upon new commits.

## Repository Map

```
Trading_bot/
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── Exchange_trade.py
├── Sharing_data.py
├── Trading_main.py
├── Trading_tools.py
├── streamlit_app.py
└── webhook_receiver.py
```

## Example Usage

- Run simulation/backtesting:
  python Trading_main.py

- Launch the trading dashboard:
  streamlit run streamlit_app.py

- Launch the webhook receiver (main file for auto-deploy):
  python webhook_receiver.py

## Getting Started

1. Install dependencies:
   pip install -r requirements.txt

2. Run the main trading script:
   python Trading_main.py

3. Start the Streamlit app:
   streamlit run streamlit_app.py

