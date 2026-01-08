import alpaca_trade_api as tradeapi
import pandas as pd
import time
from datetime import datetime

# Alpaca API credentials (use paper trading keys)
API_KEY = 'YOUR_PAPER_API_KEY'
SECRET_KEY = 'YOUR_PAPER_SECRET_KEY'
BASE_URL = 'https://paper-api.alpaca.markets'

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

# Trading parameters
SYMBOL = 'AAPL'
TIMEFRAME = '15Min'  # 15-minute bars
SHORT_WINDOW = 10    # Short-term MA window
LONG_WINDOW = 30     # Long-term MA window
QUANTITY = 1         # Shares to trade

def get_historical_data(symbol, timeframe, limit):
    """Fetch historical price data from Alpaca"""
    bars = api.get_bars(symbol, timeframe, limit=limit).df
    return bars['close']

def calculate_moving_averages(prices, short_window, long_window):
    """Calculate short and long moving averages"""
    short_ma = prices.rolling(window=short_window).mean()
    long_ma = prices.rolling(window=long_window).mean()
    return short_ma.iloc[-1], long_ma.iloc[-1]

def check_positions(symbol):
    """Check if we have an existing position"""
    try:
        position = api.get_position(symbol)
        return int(position.qty)
    except:
        return 0

def place_order(symbol, qty, side):
    """Place a market order"""
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        print(f"{datetime.now()}: {side.upper()} {qty} shares of {symbol}")
    except Exception as e:
        print(f"Order failed: {e}")

def main():
    print("Starting trading bot...")
    while True:
        try:
            # Get current positions
            current_position = check_positions(SYMBOL)
            
            # Fetch latest price data
            prices = get_historical_data(SYMBOL, TIMEFRAME, LONG_WINDOW + 10)
            
            # Calculate moving averages
            short_ma, long_ma = calculate_moving_averages(prices, SHORT_WINDOW, LONG_WINDOW)
            
            # Generate signals
            if short_ma > long_ma and current_position <= 0:
                # Buy signal
                place_order(SYMBOL, QUANTITY, 'buy')
            elif short_ma < long_ma and current_position > 0:
                # Sell signal
                place_order(SYMBOL, abs(current_position), 'sell')
            
            # Wait before next iteration (adjust based on your timeframe)
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\nStopping bot...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
