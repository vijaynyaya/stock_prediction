# Stock Price Direction Predictor

A machine learning-based API for predicting stock price movements using historical market data.

## Project Overview

This project implements a FastAPI application that predicts whether a stock's price will move UP or DOWN on the next trading day. It uses a machine learning model trained on historical stock data with various engineered features.

## Features

- **Stock Movement Prediction**: Predicts whether a stock's price will go up or down on the next trading day
- **Confidence Score**: Provides a confidence level for each prediction
- **REST API**: Simple REST API endpoints for easy integration
- **Dockerized Deployment**: Easy deployment via Docker

## Project Structure

```
stock-price-direction-predictor/
├── app/                  # Application code
│   ├── __init__.py
│   └── main.py           # FastAPI application
├── data/                 # Data files
│   ├── raw_stock_prices.csv    # Raw stock data
│   ├── stock_features.csv      # Processed features
│   └── model.pkl               # Trained model
├── notebooks/
│   └── model_development.ipynb # Model training notebook
├── scripts/
│   ├── data_ingestion.py       # Script to get raw stock data
│   └── data_preparation.py     # Script to engineer features
├── Dockerfile            # Docker configuration
├── pyproject.toml           # Dependencies
└── README.md             # This file
```

## Prerequisites

- Python 3.9+
- [Astral-UV](https://github.com/astral-sh/uv) for dependency management
- Docker (optional, for containerized deployment)

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/vijaynyaya/stock-price-direction-predictor.git
cd stock-price-direction-predictor
```

### 2. Set up the environment with astral-uv

```bash
uv sync
```

### 3. Data Pipeline Execution

Run the following scripts in sequence to prepare the data and train the model:

```bash
# 1. Ingest raw stock data
uv run python scripts/data_ingestion.py

# 2. Process and engineer features
uv run python scripts/data_preparation.py

# 3. Train the model with the Jupyter notebook
jupyter notebook notebooks/model_development.ipynb
```

After running these steps, you should have:
- Raw stock data in `data/raw_stock_prices.csv`
- Processed features in `data/stock_features.csv`
- A trained model saved as `data/model.pkl`

## Running the API

### Local Development

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Using Docker

```bash
# Build the Docker image
docker build -t stock_price_direction_predictor .

# Run the container
docker run -d -p 127.0.0.1:8000:8000 stock_price_direction_predictor
```

## API Endpoints

### `/`
- **Method**: GET
- **Description**: Root endpoint with basic API information

### `/health`
- **Method**: GET
- **Description**: Health check endpoint

### `/symbols`
- **Method**: GET
- **Description**: List all available stock symbols in the dataset

### `/predict/{symbol}`
- **Method**: GET
- **Description**: Get prediction for a specific stock symbol
- **Parameters**:
  - `symbol` (path parameter): Stock ticker symbol (e.g., AAPL, MSFT)
- **Response**: Prediction details including direction (UP/DOWN), confidence score, and prediction date

## Example Usage

```bash
# Get health status
curl http://localhost:8000/health

# Get list of available symbols
curl http://localhost:8000/symbols

# Get prediction for Apple Inc.
curl http://localhost:8000/predict/AAPL
```

Example response:
```json
{
  "symbol": "AAPL",
  "prediction": "UP",
  "confidence": 0.78,
  "predicted_date": "2023-04-09"
}
```

## Model Details

The prediction model uses the following features:
- Daily return
- 5-day moving average
- 10-day volatility
- Volume spike ratio
- Day of week
- Previous day's closing price
- High-low range

## Next Steps and Improvements

- Add support for date range filtering
- Implement automated retraining pipeline
