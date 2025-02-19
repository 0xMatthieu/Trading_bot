from Exchange_trade import Exchange
import Trading_tools
from Evaluate_strategy import fetch_and_store_historical_data
import glob
import json
import openai

def process_symbol_data(symbol: str) -> dict:
    """
    Process data files corresponding to the input symbol and get AI analysis.

    Looks for files in ./data matching pattern like SYMBOL_TIMEFRAME.json
    (where symbol is converted by replacing '/' with '_') and sends their contents
    to an OpenAI API prompt. The prompt instructs for a structured output in JSON.
    """
    pattern = f"data/{symbol.replace('/', '_')}_*.json"
    matched_files = glob.glob(pattern)
    contents = {}
    for file in matched_files:
        with open(file, 'r', encoding='utf-8') as f:
            contents[file] = f.read()
    prompt = f\"\"\"Analyze the following data files and output a structured summary.
Return a JSON with keys 'symbol', 'summary', and 'data_count'.

Data: {json.dumps(contents)}\"\"\"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that outputs answers only in valid JSON."},
            {"role": "user", "content": prompt}
        ]
    )
    response_text = response.choices[0].message.content
    try:
        result_json = json.loads(response_text)
    except Exception as e:
        result_json = {"error": "Failed to parse AI response", "response_text": response_text}
    return result_json

if __name__ == "__main__":
    exchange = Exchange(name='kucoin')
    timeframes = ['1h', '4h', '1d', '1w', '1M']
    symbol = 'BTC/USDT'
    for timeframe in timeframes:
        df = fetch_and_store_historical_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=1000, market_type='spot')
        df = Trading_tools.calculate_ema(df)
        file_path = f"data/{symbol.replace('/', '_')}_{timeframe}.json"
        df.to_json(file_path, orient='records', date_format='iso')
