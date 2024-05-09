import pandas as pd
import yfinance as yf
import pandas_ta as ta
import matplotlib.pyplot as plt

# Define the stock symbol and time period
symbol = "AAPL"
start_date = "2022-01-01"
end_date = "2022-12-31"

# Download historical stock data
stock_data = yf.download(symbol, start=start_date, end=end_date)

# Calculate 10-day simple moving average of volume
stock_data['Volume_SMA10'] = ta.sma(stock_data['Volume'], length=10)

# Filter DataFrame for accumulation points
accumulation_points = stock_data[stock_data['Volume'] > stock_data['Volume_SMA10']]

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(stock_data['Close'], label='Close Price', color='blue')
plt.scatter(accumulation_points.index, accumulation_points['Close'], 
            label='Accumulation', color='green', marker='^')
# plt.plot(stock_data['Volume_SMA10'], label='10-day SMA', color='orange')  # Add SMA line

plt.title(f'{symbol} Stock Price with Accumulation Points')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
