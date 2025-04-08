#%%
from stocks_api import FinancialModelingPrepClient
import os
import pandas as pd
from pathlib import Path
#%%
FMP_API_KEY = os.environ.get("FMP_API_KEY", None)
if FMP_API_KEY is None:
    raise Exception("FMP_API_KEY is required")
api_client = FinancialModelingPrepClient(api_key="HHkQADZfxmBxMyxB3doGndbgX57Ohj9q")
#%%
SAMPLE_TICKERS = [
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOG',
    'GOOGL', 'META', 'JNJ', 'NFLX', 'TSLA',
    'TSM', 'AVGO', 'WMT', 'LLY', 'V',
    'JPM', 'UNH', 'XOM', 'MA', 'COST'
]
#%%
start_date = "2021-01-01" # max last five years
data = list()
for ticker in SAMPLE_TICKERS:
    try:
        res = api_client.get_historical_price(ticker, from_date=start_date)
        df = pd.DataFrame(res)
        data.append(df)
    except Exception as e:
        # GOOG, AVGO, LLY, and MA are premium tickers
        print("Couldn't get {0}".format(ticker,))
        print(e)

df = pd.concat(data)
df.columns = ["symbol","date","open","high","low","close","volume"]
# %%
dest_path = Path(__file__).parents[1] / "data" / "raw_stock_prices.csv"
df.to_csv(dest_path.as_posix(), index=False)
# %%
