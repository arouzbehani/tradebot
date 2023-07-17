# from pprint import pp
import requests
import tradermade as tm

url = "https://marketdata.tradermade.com/api/v1/live"
currency = "USDJPY,GBPUSD,UK100"
api_key = "api_key"

querystring = {"currency":currency,"api_key":api_key}

response = requests.get(url, params=querystring)

print(response.json())
