import os
from pathlib import Path
import kucoinMarkets as kc
import pandas as pd

BASE_DIR = '/root/trader_webapp'

def GetMarkets(tf,exchangeName='Kucoin',relp=False, testdata=False):
    t=0
    markets={}
    rel_dir = 'Market Data/{}/{}/'.format(exchangeName,tf)
    abs_dir = os.path.join(BASE_DIR, rel_dir)
    if(relp):
        abs_dir=rel_dir
    paths = Path(abs_dir).iterdir()
    for path in paths:
        df=pd.read_csv(path)
        if(df.size>0):
            t +=1
            if(testdata) : 
                if(t>6): break
            markets[df['Coin'][0]]=df
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
