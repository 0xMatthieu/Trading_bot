from Exchange_trade import Exchange
import Trading_tools
from Evaluate_strategy import fetch_and_store_historical_data
import glob
import json
from streamlit import secrets
from openai import OpenAI
from pydantic import BaseModel

# Initialize the OpenAI API key
client = OpenAI(api_key = secrets['OPENAI_API_KEY'])

class Order(BaseModel):
    id: int
    symbol: str
    side: str
    type: str
    opened_at : str
    at_price : int
    stop_loss : int
    take_profit : int


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
    prompt = f"""Analyze the following data files and output a structured summary.
Data: {json.dumps(contents)}"""

    # Instantiate the new client (make sure your OPENAI_API_KEY is set in the environment)
    client = OpenAI()

    # Use the new chat completions endpoint
    response = client.beta.chat.completions.parse(
        model="o3-mini",  # change this to a supported model if needed
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a trading assistant. "
                    "Your role is to define the position which should be taken based on the following graphic. "
                    "Feel free to use whatever you want, do not hesitate to think about your analysis 5 times to improve your understanding. "
                    "Output answers only in valid JSON. "
                    "If you decide to open a position, answer with a JSON object like that:\n\n"
                    '{'
                    ' "id": 1,'
                    ' "symbol": "BTC/USDT",'
                    ' "type" : "limit"'
                    ' "side": "Long",'
                    ' "opened_at": "19/02/2025 - 13:55",'
                    ' "at_price": 95535,'
                    ' "stop_loss": 94000,'
                    ' "take_profit": 99000'
                    '}'
                )
            },
            {"role": "user", "content": prompt},

        ],
        response_format=Order,
    )

    response_text = response.choices[0].message.parsed
    try:
        result_json = response_text
    except Exception as e:
        result_json = {"error": "Failed to parse AI response", "response_text": response_text}
    return result_json

if __name__ == "__main__":
    exchange = Exchange(name='kucoin')
    timeframes = ['1h', '4h', '1d', '1w', '1M']
    symbol = 'BTC/USDT'
    """
    for timeframe in timeframes:
        df = fetch_and_store_historical_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=100, market_type='spot', erase=True)
        df = Trading_tools.calculate_ema(df)
        file_path = f"data/{symbol.replace('/', '_')}_{timeframe}.json"
        df.to_json(file_path, orient='records', date_format='iso')
    """
    answer = process_symbol_data(symbol=symbol)
    print(answer)
