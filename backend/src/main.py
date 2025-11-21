# backend/src/main.py

import yfinance as yf
from datetime import datetime, timedelta

print("Backend application started.")

def fetch_daily_kline(symbol: str):
    """
    Fetches daily K-line data for a given stock symbol using yfinance.
    """
    print(f"Fetching daily K-line for {symbol}...")
    try:
        # Fetch data for the last 5 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7) # Fetch a bit more to ensure 5 trading days

        stock_data = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

        if not stock_data.empty:
            print(f"Successfully fetched K-line data for {symbol}:")
            print(stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5)) # Display last 5
            return stock_data
        else:
            print(f"No K-line data found for {symbol}.")
            return None
    except Exception as e:
        print(f"Error fetching K-line data for {symbol}: {e}")
        return None

def main():
    fetch_daily_kline("AAPL")

if __name__ == "__main__":
    main()

