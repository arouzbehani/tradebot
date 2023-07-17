import requests
import config as conf
api_key = conf.BING_API_KEY
secret_key = conf.BING_SECRET_KEY

url = "https://api.bingx.com/v1/swap/market/get_kline_history?symbol=BTC-USDT&interval=1m&limit=1000"

headers = {
    "X-BingX-API-Key": api_key,
    "X-BingX-API-Secret": secret_key,
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(response.status_code)