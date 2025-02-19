from Exchange_trade import Exchange
import Trading_tools
from Evaluate_strategy import fetch_and_store_historical_data

if __name__ == "__main__":
    exchange = Exchange(name='kucoin')
    timeframes = ['1h', '4h', '1d', '1w', '1M']
    symbol = 'BTC/USDT'
    for timeframe in timeframes:
        df = fetch_and_store_historical_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=1000, market_type='spot')
        df = Trading_tools.calculate_ema(df)
        file_path = f"data/{symbol.replace('/', '_')}_{timeframe}.json"
        df.to_json(file_path, orient='records', date_format='iso')