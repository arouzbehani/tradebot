import os , GLOBAL
from pathlib import Path
import kucoinMarkets as kc
import YahooMarket as ym
import pandas as pd


def GetMarkets(tf,exchangeName='Kucoin',relp=False, testdata=False):
    t=0
    markets={}
    rel_dir = 'Market Data/{}/{}/'.format(exchangeName,tf)
    abs_dir = os.path.join(GLOBAL.BASE_DIR, rel_dir)
    if(relp):
        abs_dir=rel_dir
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
def ReadKucoinMarket(timeframes,testdata=False,relp=False):
    markets = []
    for i in range(0, len(timeframes)):
        markets = kc.GetMarkets()
        marketsegment = {k: markets[k] for k in ('ADA/USDT', 'BTC/USDT')}
        if(testdata):
            datframes, e = kc.GetMarketData(marketsegment, timeframes[i], 'All', 350,relp=relp)
        else :
            datframes, e = kc.GetMarketData(markets, timeframes[i], 'All', 350,relp=relp)

def ReadYahooMarket(timeframes,testdata=False,local=False):
    markets = []
    dict={"1d":100, '5m':59 , '1wk':100,
           "15m" :59 , "30m":59 , "60m":59 , "90m":59 }
    for i in range(0, len(timeframes)):
        markets = ym.GetMarkets(local)
        marketsegment = {k: markets[k] for k in (0, 1)}
        if(testdata):
            datframes, e = ym.GetMarketData(marketsegment,period=dict[timeframes[i]],symbol='All', tf= timeframes[i],relp=local)
        else :
            datframes, e = ym.GetMarketData(markets, period=dict[timeframes[i]],symbol='All', tf= timeframes[i],relp=local)
