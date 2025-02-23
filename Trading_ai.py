from Exchange_trade import Exchange
import Trading_tools
from Evaluate_strategy import fetch_and_store_historical_data
import glob
import json
from streamlit import secrets
from openai import OpenAI
from pydantic import BaseModel, Field

# Initialize the OpenAI API key
client = OpenAI(api_key = secrets['OPENAI_API_KEY'])

class Order(BaseModel):
    id: int = Field(..., description="Unique id of the trade, shall be always greater than the previous one")
    symbol: str = Field(..., description="The crypto symbol. It is available in the data given in the prompt. Example BTC/USDT")
    side: str = Field(..., description="Only 2 values possible, short or long")
    type: str = Field(..., description="The order type can be limit or market")
    opened_at : str = Field(..., description="The current time")
    at_price : int = Field(..., description="The price to open the trade, market price or limit price")
    stop_loss : int = Field(..., description="Trade stop loss")
    take_profit : int = Field(..., description="Trade take profit")

class CurrencyOrderList(BaseModel):
    symbol: str = Field(..., description="The crypto symbol. It is available in the data given in the prompt. Example BTC/USDT")
    orders: list[Order] = Field(..., description="List of orders to take")

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
    prompt = f"""Analyze the following data files and output orders you would take.
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
                    """You are a trading assistant.
                    Your role is to define the position which should be taken based on the following graphic. You can provide up to 3 orders
                    Feel free to use whatever you want, do not hesitate to think about your analysis 5 times to improve the outcome. """
                )
            },
            {"role": "user", "content": prompt},

        ],
        response_format=CurrencyOrderList,
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

    for timeframe in timeframes:
        df = fetch_and_store_historical_data(exchange=exchange, symbol=symbol, timeframe=timeframe, limit=100, market_type='spot', erase=True)
        df = Trading_tools.calculate_ema(df)
        file_path = f"data/{symbol.replace('/', '_')}_{timeframe}.json"
        df.to_json(file_path, orient='records', date_format='iso')

    answer = process_symbol_data(symbol=symbol)
    print(answer)
