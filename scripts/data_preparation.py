#%%
import pandas as pd
from pathlib import Path
# %%
DATA_DIR = Path(__file__).parents[1] / "data"
SRC_PATH = DATA_DIR / "raw_stock_prices.csv"
DEST_PATH = DATA_DIR / "stock_features.csv"
df = pd.read_csv(SRC_PATH.as_posix())
df["date"] = pd.to_datetime(df["date"])
# %%
def compute_features(symbol_df: pd.DataFrame):
    df = symbol_df.sort_values(by="date").copy()
    # Daily Return
    df["daily_return"] = (df["close"] - df["open"]) / df["open"]
    # 5-day Moving Avergage (close)
    df["ma_5"] = df["close"].rolling(5).mean()
    # 10-day Rolling Volatility (standard deviation of close)
    df["volatility_10"] = df["close"].rolling(10).std()
    # Volume Spike
    df["volume_spike"] = df["volume"] / df["volume"].rolling(5).mean()
    # Day of Week
    df["day_of_week"] = df["date"].dt.day_of_week
    # Lag-1 Close, previous day's closing price
    df["lag_close_1"] = df["close"].shift(1)
    # High-Low Range
    df["hl_range"] = (df["high"] - df["low"]) / df["low"]
    # Next Day's Closing Price
    df["next_day_close"] = df["close"].shift(-1)
    # Creating a binary target variable `price_up` (1 if tomorrow's close > today's close, 0 otherwise)
    df["price_up"] = (df["next_day_close"] > df["close"]).astype(int)
    return df.dropna()
# %%
features_df = df.groupby("symbol").apply(compute_features).reset_index(drop=True)
# %%
features_df.to_csv(DEST_PATH.as_posix(), index=False)
