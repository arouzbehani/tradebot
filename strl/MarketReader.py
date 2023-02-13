import GLOBAL,gc
from pathlib import Path
import kucoinMarkets as kc
import YahooMarket as ym
import pandas as pd


def GetMarkets(tf,exchangeName='Kucoin',local=False, testdata=False):
    t=0
    markets={}
    rel_dir = 'Market Data/{}/{}/'.format(exchangeName,tf)
    abs_dir =GLOBAL.ABSOLUTE(rel_dir,local)
    paths = Path(abs_dir).iterdir()
    for path in paths:
        try:
            df=pd.read_csv(path)
            if(df.size>0):
                t +=1
                if(testdata) : 
                    if(t>6): break
                if('Coin' in df.columns):
                    markets[df['Coin'][0]]=df
                elif('Symbol' in df.columns):
                    markets[df['Symbol'][0]]=df
        except:
            continue
    return markets 
def ReadKucoinMarket(timeframes,testdata=False,local=False,symbol=''):
    markets = []
    markets = kc.GetMarkets()
    for i in range(0, len(timeframes)):
        marketsegment = {k: markets[k] for k in ('ADA/USDT', 'BTC/USDT')}
        if symbol !='':
            testdata=True
            marketsegment = {k: markets[k] for k in (symbol,)}

        if(testdata):
            datframes, e = kc.GetMarketData(marketsegment, timeframes[i], 'All', 1200,local=local)
            del datframes
            del e
            gc.collect()
        else :
            datframes, e = kc.GetMarketData(markets, timeframes[i], 'All', 1200,local=local)
            del datframes
            del e
            gc.collect()
        del marketsegment
        gc.collect()
    del markets
    gc.collect()

def ReadYahooMarket(timeframes,testdata=False,local=False,symbol=''):
    markets = []
    dict={"1d":100, '5m':59 , '1wk':100,
           "15m" :59 , "30m":59 , "60m":59 , "90m":59 }
    for i in range(0, len(timeframes)):
        markets = ym.GetMarkets(local)
        if symbol !='':
            testdata=True
            marketsegment = [x for x in markets if x.lower().__contains__(symbol.lower())]
        if(testdata):
            datframes, e = ym.GetMarketData(marketsegment,period=dict[timeframes[i]],symbol='All', tf= timeframes[i],local=local)
            del datframes
            del e
            gc.collect()
       
        else :
            datframes, e = ym.GetMarketData(markets, period=dict[timeframes[i]],symbol='All', tf= timeframes[i],local=local)
            del datframes
            del e
            gc.collect()
      
        del markets
        gc.collect()

