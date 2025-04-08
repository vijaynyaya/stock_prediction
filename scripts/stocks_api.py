import requests
from typing import List, Dict, Any
import time


class AlphaVantageClient:
    """
    A simplified client for interacting with the Alpha Vantage API.
    
    This class provides basic methods to fetch daily time series data and stock quotes.
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str, rate_limit_per_min: int = 5):
        """
        Initialize the Alpha Vantage API client.
        
        Args:
            api_key: Your Alpha Vantage API key
            rate_limit_per_min: Maximum number of requests per minute (default: 5)
        """
        self.api_key = api_key
        self.rate_limit = rate_limit_per_min
        self.last_request_time = 0
    
    def _enforce_rate_limit(self) -> None:
        """Enforce the rate limit by waiting if necessary."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit
        
        if time_since_last_request < min_interval:
            time.sleep(min_interval - time_since_last_request)
            
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a request to the Alpha Vantage API.
        
        Args:
            params: Dictionary of query parameters
            
        Returns:
            JSON response data as a dictionary
            
        Raises:
            Exception: If the API request fails
        """
        self._enforce_rate_limit()

        # Add API key to parameters
        params['apikey'] = self.api_key
        
        response = requests.get(self.BASE_URL, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check for API error messages
        if "Error Message" in data:
            raise Exception(f"API error: {data['Error Message']}")
        
        return data
    
    def get_daily_time_series(self, symbol: str, output_size: str = 'compact') -> Dict[str, Any]:
        """
        Get daily time series data for a given symbol.
        
        Args:
            symbol: The stock symbol (e.g., 'IBM', 'AAPL')
            output_size: 'compact' (latest 100 data points) or 'full' (up to 20 years of data)
            
        Returns:
            Dictionary containing the time series data
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': output_size
        }
        
        return self._make_request(params)
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest price and volume information for a security of your choice.
        
        Args:
            symbol: The stock symbol (e.g., 'IBM', 'AAPL')
            
        Returns:
            Dictionary containing the quote data
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        return self._make_request(params)
    
    def search_symbol(self, keywords: str) -> List[Dict[str, str]]:
        """
        Search for a symbol based on keywords.
        
        Args:
            keywords: Keywords to search for
            
        Returns:
            List of matching symbols and their details
        """
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords
        }
        
        data = self._make_request(params)
        return data.get('bestMatches', [])

import requests
from typing import Dict, Any, Optional, List


class FinancialModelingPrepClient:
    """
    A client for interacting with the Financial Modeling Prep API.
    
    This class provides methods to fetch non-split-adjusted historical price data.
    """
    
    BASE_URL = "https://financialmodelingprep.com/stable"
    
    def __init__(self, api_key: str):
        """
        Initialize the Financial Modeling Prep API client.
        
        Args:
            api_key: Your Financial Modeling Prep API key
        """
        self.api_key = api_key
    
    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a request to the Financial Modeling Prep API.
        
        Args:
            endpoint: API endpoint path
            params: Dictionary of query parameters
            
        Returns:
            JSON response data as a dictionary
            
        Raises:
            Exception: If the API request fails
        """
        # Add API key to parameters
        params['apikey'] = self.api_key
        
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
        
        data = response.json()
        
        # Check for empty response
        if not data and isinstance(data, list):
            print(f"Warning: Empty response received. Check symbol and date range.")
        
        return data
    
    def get_historical_price(self, 
                           symbol: str, 
                           from_date: Optional[str] = None, 
                           to_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get non-split-adjusted historical stock prices for a given symbol with optional date range.
        
        Args:
            symbol: The stock symbol (e.g., 'AAPL', 'MSFT')
            from_date: Start date in 'YYYY-MM-DD' format (optional)
            to_date: End date in 'YYYY-MM-DD' format (optional)
            
        Returns:
            List of dictionaries containing historical price data
        """
        endpoint = "/historical-price-eod/non-split-adjusted"
            
        # Build parameters
        params = {
            'symbol': symbol
        }
        
        # Add optional date range parameters
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        return self._make_request(endpoint, params)