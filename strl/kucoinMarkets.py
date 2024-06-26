import ccxt

import config
import pandas as pd
import os,gc
import GLOBAL as GLOBAL

exchange = ccxt.kucoin({
    'apikey': config.Kucoin_API_Key,
    'secret': config.kucoin_API_Secret
})


def GetMarkets():
    return exchange.load_markets()
def GetMarketData(markets,tf='1d', coin='All', lim=500, paircoin='/USDT',local=False):
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
                rel_path='Market Data/Kucoin/{}/{}__{}.csv'.format(tf,m.replace('/','_'),tf)
                abs_path =GLOBAL.ABSOLUTE(rel_path,local)
                if(os.path.isfile(abs_path)):
                    df0=pd.read_csv(abs_path)
                    fdf=pd.concat([df[:-1],df0]).drop_duplicates().sort_values(by=['timestamp'])
                    fdf.to_csv(abs_path, header=True, index=False, sep=',', mode='w')
                    del df0
                    del fdf
                    gc.collect()
                else:
                    fdf=df[:-1]
                    fdf.to_csv(abs_path, header=True, index=False, sep=',', mode='w')
                    del fdf
                    gc.collect()

                marketData.append(df)
                del df
                gc.collect()

            except:
                print('error in fetching market data for: ' + m + ' --- tf:'+tf)
                errordata.append(m + ':' + tf)
    return (marketData, errordata)

# markets=(exchange.load_markets())
# for m in markets:
#     print (markets[m])
#     break