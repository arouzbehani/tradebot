import datetime
import os
from pathlib import Path
import time
import kucoinMarkets as kc
import talibHelper as tah
import yfinance as yf
import pandas as pd
import breakout as bro

class MarketData(object):
    def __init__(self):
        self._Coin = None
        self._TimeFrame = None
        self._Data = []

    @property
    def Coin(self):
        return self._Coin

    @Coin.setter
    def Coin(self, value):
        self._Coin = value

    @property
    def TimeFrame(self):
        return self._TimeFrame

    @TimeFrame.setter
    def TimeFrame(self, value):
        self._TimeFrame = value

    @property
    def Data(self):
        return self._Data

    @Data.setter
    def Data(self, value):
        self._Data = value

def FindSignals_01(maxdelay_min, timeframes, testdata=False):
    kucoinmarkets = []
    latestSignals = []
    # timeframes = ['5m', '15m', '1h', '4h', '1d', '1w']
    errors = []
    markets = []
    datframes = []

    for i in range(0, len(timeframes)):
        if (timeframes == '1d'):
            maxdelay_min = 7*24*60
        markets = kc.GetMarkets()
        marketsegment = {k: markets[k] for k in ('ADA/USDT', 'BTC/USDT')}
        if (testdata):
            datframes, e = kc.GetMarketData(
                marketsegment, timeframes[i], 'All', 350)
        else:
            datframes, e = kc.GetMarketData(markets, timeframes[i], 'All', 350)

        now = datetime.datetime.now()
        now_timestamp = time.time() - maxdelay_min*60

        errors.append(e)
        for df in datframes:

            md = MarketData()
            if (len(df['Coin']) > 0):
                md.Coin = df['Coin'][0]
            else:
                md.Coin = 'ND'
            md.TimeFrame = timeframes[i]

            try:
                # res , md.Data = tah.MorningStars(df)
                res2, alld = tah.AllPatterns(df[:-1])
                if (res2):
                    latest = alld.loc[(alld['timestamp'] >=
                                       now_timestamp*1000)].tail(1)

                    latestSignals.append(latest)

                    # latest.to_csv(md.Coin.replace('/','_')+"___"+md.TimeFrame+".csv", header=True, index=True, sep=',', mode='w')
                # if(res):
                #     kucoinmarkets.append(md)
            except:
                print('Error in finding signal : ' +
                      md.TimeFrame + "___"+md.Coin)
           # md.Data = df
            rel_path = "TA-Lib Signals/"+timeframes[i]+"/" + \
                timeframes[i] + "__" + \
                now.strftime("%d_%m_%Y__%H_%M_%S")+".csv"

            BASE_DIR = '/root/trader_webapp'
            abs_path = os.path.join(BASE_DIR, rel_path)
            # abs_path=rel_path
            if (len(latestSignals) > 0):
                signalsdf = pd.concat(latestSignals)

                signalsdf.to_csv(abs_path, header=True,
                                 index=True, sep=',', mode='w')


def br_check(c,tf,exch,candles,percentage,relp):
    if bro.is_coin_breaking_out(c,tf,exch,candles,percentage,relp):
        return 'Breaking Out'
    return ''
def TALibPattenrSignals(maxdelay_min, timeframes, markets, exchangeName='Kucoin',relp=False,brout_candles=15,brout_percentage=2):
    latestSignals = []
    

    for i in range(0, len(timeframes)):
        now_timestamp = time.time() - maxdelay_min*60
        now = datetime.datetime.now()

        for m in markets:
            print("Finding Signals for Market : {} __ Timeframe:{}".format(
                m, timeframes[i]))
            df = markets[m]
            
            try:
                res2, alld = tah.AllPatterns(df)
                if (res2):
                    latest = alld.loc[(alld['timestamp'] >=
                                       now_timestamp*1000)].tail(1)
                    latestSignals.append(latest)
            except:
                print('Error in finding signal : {}___{}'.format(
                    timeframes[i], m))
        rel_path = "TA-Lib Signals/{}/{}/{}__{}.csv".format(
            exchangeName, timeframes[i], timeframes[i], now.strftime("%d_%m_%Y__%H_%M_%S"))
        BASE_DIR = '/root/trader_webapp'
        abs_path = os.path.join(BASE_DIR, rel_path)
        if(relp):
            abs_path=rel_path

        if (len(latestSignals) > 0):
            signalsdf = pd.concat(latestSignals)
            signalsdf['breaking out']=signalsdf['Coin'].apply(br_check,exch=exchangeName, tf=timeframes[i],candles=brout_candles,percentage =brout_percentage ,relp=relp)
            signalsdf.to_csv(abs_path, header=True,
                             index=True, sep=',', mode='w')
