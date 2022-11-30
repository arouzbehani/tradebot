import ccxt
import config
import pandas as pd

exchange = ccxt.kucoin({
    'apikey': config.Kucoin_API_Key,
    'secret': config.kucoin_API_Secret
})


def GetMarketData(tf='1d', coin='All', lim=500,paircoin='/USDT'):
    marketData = []

    markets = exchange.load_markets()
    if (coin != 'All'):
        simple = [t for t in markets if t == coin]
        markets = simple

    for m in markets:
        if m.endswith(paircoin):
            try:
                bars = exchange.fetch_ohlcv(m, limit=lim, timeframe=tf)
                df = pd.DataFrame(bars, columns=['timestamp',
                                                 'open', 'high', 'low', 'close', 'volume'])
                marketData.append(df)
            except:
                print('error in fetch ' + m)
    return marketData
