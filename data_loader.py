import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import random

def get_sp500_symbols():
    """
    Gets a list of S&P 500 ticker symbols
    
    Returns:
        list: List of ticker symbols
    """
    try:
        # Get S&P 500 tickers from Wikipedia
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'wikitable', 'id': 'constituents'})
        
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.strip()
            tickers.append(ticker)
            
        return tickers
        
    except Exception as e:
        # If scraping fails, return a smaller list of popular S&P 500 stocks
        return ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "JPM", "JNJ", "V", 
                "PG", "UNH", "HD", "MA", "DIS", "BAC", "ADBE", "CRM", "NFLX", "CMCSA"]

def fetch_stock_data(ticker, period="1y"):
    """
    Fetches stock data from Yahoo Finance and ensures it has the required columns.

    Args:
        ticker (str): Stock ticker symbol
        period (str): Time period for data (default: 1y = 1 year)

    Returns:
        pd.DataFrame: DataFrame with stock price data

    Raises:
        Exception: If required columns are missing or data cannot be fetched
    """
    try:
        # Add random sleep to avoid rate limiting
        time.sleep(random.uniform(0.2, 0.5))

        # Fetch data from Yahoo Finance
        stock_data = yf.download(ticker, period=period, progress=False)

        # Debug: Print the fetched data and column names
        print(f"Fetched data for {ticker}: \n{stock_data.head()}")
        print(f"Columns in fetched data: {stock_data.columns}")

        # Flatten the multi-level column index (if present)
        if isinstance(stock_data.columns, pd.MultiIndex):
            stock_data.columns = stock_data.columns.map('_'.join).str.strip('_')

        # Strip the ticker suffix from column names (e.g., "Open_ADSK" -> "Open")
        stock_data.columns = stock_data.columns.str.replace(f"_{ticker}", "", regex=False)

        # Debug: Print the column names after flattening and stripping
        print(f"Columns after flattening and stripping: {stock_data.columns}")

        # Define a mapping of possible Yahoo Finance column names to expected names
        column_mapping = {
            'Open': 'Price_Open',
            'High': 'Price_High',
            'Low': 'Price_Low',
            'Close': 'Price_Close',
            'Adj Close': 'Price_Close',  # Handle 'Adj Close' if present
            'Volume': 'Price_Volume'
        }

        # Rename columns based on the mapping
        stock_data = stock_data.rename(columns={k: v for k, v in column_mapping.items() if k in stock_data.columns})

        # Debug: Print the column names after renaming
        print(f"Columns after renaming: {stock_data.columns}")

        # Ensure the DataFrame has the required columns
        required_columns = ['Price_Open', 'Price_High', 'Price_Low', 'Price_Close', 'Price_Volume']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Reset index to make Date a column and ensure it's not a DatetimeIndex
        stock_data = stock_data.reset_index()

        # Ensure there are enough data points for pattern detection
        if len(stock_data) < 30:
            raise ValueError(f"Not enough data points for {ticker} (minimum 30 required)")

        # Add some technical indicators that will be useful for pattern detection
        # 20-day and 50-day moving averages
        stock_data['MA20'] = stock_data['Price_Close'].rolling(window=20).mean()
        stock_data['MA50'] = stock_data['Price_Close'].rolling(window=50).mean()

        # Calculate daily price changes and volatility
        stock_data['Daily_Return'] = stock_data['Price_Close'].pct_change()
        stock_data['Volatility'] = stock_data['Daily_Return'].rolling(window=20).std()

        # Add ticker column for reference
        stock_data['Ticker'] = ticker

        return stock_data

    except Exception as e:
        raise Exception(f"Error fetching data for {ticker}: {str(e)}")