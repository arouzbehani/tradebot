import ccxt
import config
import pandas as pd

exchange = ccxt.kucoin({
    'apikey': config.Kucoin_API_Key,
    'secret': config.kucoin_API_Secret
})

def GetMarkets():
    return exchange.load_markets()
def GetMarketData(markets,tf='1d', coin='All', lim=500, paircoin='/USDT'):
    marketData = []
    errordata = []

    #markets = exchange.load_markets()
    if (coin != 'All'):
        simple = [t for t in markets if t == coin]
        # simple.append('ADA/USDT')
        markets = simple

    for m in markets:
        if m.endswith(paircoin):
            try:
                bars = exchange.fetch_ohlcv(m, limit=lim, timeframe=tf)
                df = pd.DataFrame(bars, columns=['timestamp',
                                                 'open', 'high', 'low', 'close', 'volume'])
                df["Coin"] = m
                marketData.append(df)
            except:
                print('error in fetch for market:' + m + ' --- tf:'+tf)
                errordata.append(m + ':' + tf)
    return (marketData, errordata)
