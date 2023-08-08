
import time
import requests
import hmac
from hashlib import sha256
import config as conf
import urllib.request
import base64

url1='https://api.bingx.com/v1/ws/uid'
APIURL = "https://open-api.bingx.com"
APIKEY = conf.BING_API_KEY
SECRETKEY = conf.BING_SECRET_KEY


def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    print("sign=" + signature)
    return signature

def genSignature(path, method, paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr = method + path + paramsStr
    return hmac.new(SECRETKEY.encode("utf-8"), paramsStr.encode("utf-8"), digestmod="sha256").digest()
def post(url, body):
    req = urllib.request.Request(url, data=body.encode("utf-8"), headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read()

def send_request(method, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
    print(url)
    headers = {
        'X-BX-APIKEY': APIKEY,
    }
    response = requests.request(method, url, headers=headers, data=payload)
    return response.text

def praseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    return paramsStr+"&timestamp="+str(int(time.time() * 1000))
def getHistoricalData():
    paramsMap = {
        "apiKey": APIKEY,
        "timestamp": int(time.time()*1000),
        "currency": "USDT",
    }
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    paramsStr += "&sign=" + urllib.parse.quote(base64.b64encode(genSignature("/api/v1/market/getHistoryKlines", "GET", paramsMap)))
    url = "%s/api/v1/market/getHistoryKlines" % APIURL
    return post(url, paramsStr)
def demo():
    payload = {}
    path = '/openApi/swap/v2/quote/ticker'
    method = "GET"
    paramsMap = {
    "symbol": "BTC-USDT"
}
    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)

def getdata():
    payload = {}
    path = '/openApi/swap/v2/quote/klines'
    method = "GET"
    paramsMap = {
    "symbol": "DOT-USDT",
    "interval":"1m",
    "limit":200
}
    paramsStr = praseParam(paramsMap)
    return send_request(method, path, paramsStr, payload)


if __name__ == '__main__':
    print("demo:", getdata())
