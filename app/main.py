from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import timedelta
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).parents[1] / "data" / "model.pkl"
STOCK_DATA_PATH = Path(__file__).parents[1] / "data" / "stock_features.csv"
FEATURE_COLUMNS = [
    "daily_return", "ma_5", "volatility_10", 
    "volume_spike", "day_of_week", "lag_close_1", "hl_range"
]

# Load the trained model
try:
    # Try to find any .pkl file with stock_direction_predictor in the name
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No model file found")
    
    MODEL = joblib.load(MODEL_PATH.as_posix())
    print(f"Loaded model: {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")
    MODEL = None


app = FastAPI(
    title="Stock Price Direction Predictor API",
    description="API for predicting whether a stock price will go up or down on the next trading day",
    version="0.0.0"
)

class PredictionResponse(BaseModel):
    symbol: str
    prediction: str
    confidence: float
    predicted_date: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


# API endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint showing API info"""
    return {
        "message": "Stock Price Direction Predictor API", 
        "usage": "Send GET request to /predict/{symbol} to get prediction"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    if MODEL is None:
        return {"status": "degraded", "message": "Model not loaded properly"}
    try:
        # Check if we can access the stock data
        if STOCK_DATA_PATH.exists():
            return {"status": "healthy", "message": "API is fully operational"}
        else:
            return {"status": "degraded", "message": "Stock data file not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/symbols", response_model=List[str])
async def get_available_symbols():
    """Get list of all available stock symbols"""
    try:
        raw_data = pd.read_csv(STOCK_DATA_PATH)
        return sorted(raw_data["symbol"].unique().tolist())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symbols: {str(e)}")
    
@app.get("/predict/{symbol}", response_model=PredictionResponse, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
async def predict(
    symbol: str,
):
    """Get prediction for a specific stock symbol with optional date range"""
    # Check if model is loaded
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please check server logs.")
    try:
        raw_data = pd.read_csv(STOCK_DATA_PATH)

        if symbol not in raw_data["symbol"].unique():
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found in the dataset")

        symbol_df = raw_data[raw_data["symbol"] == symbol]
    
        # Get the latest available data point for prediction
        latest_data = symbol_df.iloc[-1]
        
        # Extract features for prediction
        features = latest_data[FEATURE_COLUMNS].to_dict()
        features_array = np.array([list(features.values())])
        
        # Make prediction
        prediction_value = MODEL.predict(features_array)[0]
        prediction_proba = MODEL.predict_proba(features_array)[0]
        
        # Get confidence score (probability of the predicted class)
        confidence = prediction_proba[prediction_value]
        
        # Determine next trading day
        prediction_date = pd.to_datetime(latest_data["date"]) + timedelta(days=1)
        # If the next day is a weekend, adjust to Monday
        if prediction_date.dayofweek >= 5:  # 5=Saturday, 6=Sunday
            prediction_date = prediction_date + timedelta(days=7 - prediction_date.dayofweek)
            
        return {
            "symbol": symbol,
            "prediction": "UP" if prediction_value == 1 else "DOWN",
            "confidence": float(confidence),
            "predicted_date": prediction_date.strftime("%Y-%m-%d"),
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")