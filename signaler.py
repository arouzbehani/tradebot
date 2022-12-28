import datetime
import os
from pathlib import Path
import time
import kucoinMarkets as kc
import talibHelper as tah
import yfinance as yf
import pandas as pd
import breakout as bro
from ta.volatility import BollingerBands as bb
from ta.momentum import RSIIndicator as rsi
from ta.trend import EMAIndicator as ema
from ta.trend import SMAIndicator as sma
import talib  as ta


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


Base_DIR = '/root/trader_webapp/'
def ema_check(Coin, tf, exch, timeperiod=30, relp=False):
    df = None
    rel_dir = 'Market Data/{}/{}/'.format(exch, tf, Coin)
    abs_dir = os.path.join(Base_DIR, rel_dir)
    if (relp):
        abs_dir = rel_dir
    for path in Path(abs_dir).iterdir():
        if (path.name.startswith(Coin.replace('/', '_'))):
            df = pd.read_csv(path)
            break
    if (len(df) > timeperiod):
        ema_indicator_5=ema(close=df['close'],window=5,fillna=False)
        ema_indicator_10=ema(close=df['close'],window=10,fillna=False)
        ema_indicator_30=ema(close=df['close'],window=30,fillna=False)
        df['ema_5'] = ema_indicator_5.ema_indicator()
        df['ema_10'] = ema_indicator_10.ema_indicator()
        df['ema_30'] = ema_indicator_30.ema_indicator()
        last_ema_5 = df[-1:]['ema_5'].values[0]
        last_ema_10 = df[-1:]['ema_10'].values[0]
        last_ema_30 = df[-1:]['ema_30'].values[0]
        if(last_ema_30<= last_ema_10):
            if (last_ema_10 <= last_ema_5):
                return "EMA Entry Signal"
    return "No EMA Signal"

def sma_check(Coin, tf, exch, timeperiod=30, relp=False):
    df = None
    rel_dir = 'Market Data/{}/{}/'.format(exch, tf, Coin)
    abs_dir = os.path.join(Base_DIR, rel_dir)
    if (relp):
        abs_dir = rel_dir
    for path in Path(abs_dir).iterdir():
        if (path.name.startswith(Coin.replace('/', '_'))):
            df = pd.read_csv(path)
            break
    if (len(df) > timeperiod):
        sma_indicator_5=sma(close=df['close'],window=5,fillna=False)
        sma_indicator_10=sma(close=df['close'],window=10,fillna=False)
        sma_indicator_30=sma(close=df['close'],window=30,fillna=False)
        df['sma_5'] = sma_indicator_5.sma_indicator()
        df['sma_10'] = sma_indicator_10.sma_indicator()
        df['sma_30'] = sma_indicator_30.sma_indicator()
        last_sma_5 = df[-1:]['sma_5'].values[0]
        last_sma_10 = df[-1:]['sma_10'].values[0]
        last_sma_30 = df[-1:]['sma_30'].values[0]
        if(last_sma_30<= last_sma_10):
            if (last_sma_10 <= last_sma_5):
                return "SMA Entry Signal"
    return "No SMA Signal"



def PPSR(df):
    PP = pd.Series((df['high'] + df['low'] + df['close']) / 3)
    R1 = pd.Series(2 * PP - df['low'])
    S1 = pd.Series(2 * PP - df['high'])
    R2 = pd.Series(PP + df['high'] - df['low'])
    S2 = pd.Series(PP - df['high'] + df['low'])
    R3 = pd.Series(df['high'] + 2 * (PP - df['low']))
    S3 = pd.Series(df['low'] - 2 * (df['high'] - PP))
    psr = {'PP':PP, 'R1':R1, 'S1':S1, 'R2':R2, 'S2':S2, 'R3':R3, 'S3':S3}
    PSR = pd.DataFrame(psr)
    df = df.join(PSR)
    return df    
def br_check(c, tf, exch, candles, percentage, relp):
    if bro.is_coin_breaking_out(c, tf, exch, candles, percentage, relp):
        return 'Breaking Out Entry'
    return ''

def rsi_check(Coin, tf, exch, timeperiod=20, relp=False):
    df = None
    rel_dir = 'Market Data/{}/{}/'.format(exch, tf, Coin)
    abs_dir = os.path.join(Base_DIR, rel_dir)
    if (relp):
        abs_dir = rel_dir
    for path in Path(abs_dir).iterdir():
        if (path.name.startswith(Coin.replace('/', '_'))):
            df = pd.read_csv(path)
            break
    if (len(df) > timeperiod):
        rsi_indicator=rsi(close=df['close'],window=timeperiod,fillna=False)
        df['rsi'] = rsi_indicator.rsi()
        last_rsi = round(df[-1:]['rsi'].values[0],1)
        if(last_rsi<=30):
            return 'Entry rsi: {}'.format(last_rsi)
        if(last_rsi>=70):
            return 'Exit rsi: {}'.format(last_rsi)
        else:
            return 'No rsi Signal: {}'.format(last_rsi)

def boll_check(Coin, tf, exch, timeperiod=20, nstdv=2, relp=False):
    df = None
    rel_dir = 'Market Data/{}/{}/'.format(exch, tf, Coin)
    abs_dir = os.path.join(Base_DIR, rel_dir)
    if (relp):
        abs_dir = rel_dir
    for path in Path(abs_dir).iterdir():
        if (path.name.startswith(Coin.replace('/', '_'))):
            df = pd.read_csv(path)
            break
    if (len(df) > timeperiod):


        indicator_bb = bb(close=df['close'], window=timeperiod,
                          window_dev=nstdv, fillna=False)
        df['upperband'] = indicator_bb.bollinger_hband()
        df['middleband'] = indicator_bb.bollinger_mavg()
        df['lowerband'] = indicator_bb.bollinger_lband()
        df['bandwidth'] = indicator_bb.bollinger_wband()
        df['pband'] = indicator_bb.bollinger_pband()
        last_close = df[-1:]['close'].values[0]
        last_lowerband = df[-1:]['lowerband'].values[0]
        last_upperband = df[-1:]['upperband'].values[0]
        one_to_last_close = df[-2:-1]['close'].values[0]
        one_to_last_lowerband = df[-2:-1]['lowerband'].values[0]
        one_to_last_upperband = df[-2:-1]['upperband'].values[0]
        one_to_last_pband = df[-2:-1]['pband'].values[0]

        if (one_to_last_close < one_to_last_lowerband):
            if (last_close > last_lowerband):
                return "BB Entry Signal"
            if (last_close < last_lowerband and one_to_last_pband < 0):
                return "BB Squeez Exit Signal"

        elif (one_to_last_close > one_to_last_upperband):
            if (last_close > last_upperband and one_to_last_pband >= 1):
                return "BB Squeez Entry Signal"

            if (last_close < last_upperband):
                return "BB Exit Signal"
    return "No BB Signal"
def count_entry(s:str):
    try:
        if(s.lower().__contains__('entry')):
            return 1
    except:
        print('Error in counting Entry: {}'.format(str(s)))
        return 0
    return 0

def TALibPattenrSignals(maxdelay_min, timeframes, markets, exchangeName='Kucoin', relp=False, brout_candles=15, brout_percentage=2,read_patterns=False):
    latestSignals = []

    for i in range(0, len(timeframes)):
        now_timestamp = time.time() - maxdelay_min*60
        now = datetime.datetime.now()

        for m in markets:
            print("Finding Signals for Market : {} __ Timeframe:{}".format(
                m, timeframes[i]))
            df = markets[m]
            if(read_patterns):
                try:
                    res2, alld = tah.AllPatterns(df)
                    if (res2):
                        latest = alld.loc[(alld['timestamp'] >=
                                        now_timestamp*1000)].tail(1)
                        latestSignals.append(latest)
                except:
                    print('Error in finding signal : {}___{}'.format(
                        timeframes[i], m))
            else:
                    df['date time'] = pd.to_datetime(df['timestamp'], unit='ms')
                    alld=(pd.DataFrame(data=df).sort_values(by=['timestamp']))
                    latest = alld.loc[(alld['timestamp'] >=
                                        now_timestamp*1000)].tail(1)
                    latestSignals.append(latest)


        rel_path = "TA-Lib Signals/{}/{}/{}__{}.csv".format(
            exchangeName, timeframes[i], timeframes[i], now.strftime("%d_%m_%Y__%H_%M_%S"))
        BASE_DIR = '/root/trader_webapp'
        abs_path = os.path.join(BASE_DIR, rel_path)
        if (relp):
            abs_path = rel_path

        if (len(latestSignals) > 0):
            signalsdf = pd.concat(latestSignals)

            signalsdf['breaking out'] = signalsdf['Coin'].apply(
                br_check, exch=exchangeName, tf=timeframes[i], candles=brout_candles, percentage=brout_percentage, relp=relp)
            signalsdf['bollinger'] = signalsdf['Coin'].apply(
                boll_check, exch=exchangeName, tf=timeframes[i], timeperiod=20, nstdv=2, relp=relp)
            signalsdf['rsi'] = signalsdf['Coin'].apply(
                rsi_check, exch=exchangeName, tf=timeframes[i], timeperiod=14, relp=relp)
            signalsdf['ema'] = signalsdf['Coin'].apply(
                ema_check, exch=exchangeName, tf=timeframes[i], timeperiod=30, relp=relp)
            signalsdf['sma'] = signalsdf['Coin'].apply(
                sma_check, exch=exchangeName, tf=timeframes[i], timeperiod=30, relp=relp)

            scols=['breaking out','bollinger','rsi','ema','sma']
            signalsdf['entry']=0
            for s in scols:
                signalsdf['entry'] +=signalsdf[s].map(count_entry)
            signalsdf=signalsdf.sort_values(by=['entry'],ascending=False)
            signalsdf.to_csv(abs_path, header=True,
                             index=True, sep=',', mode='w')


def test():
    return "signaler"


def MakeBollingerBandsSignals(market='Kucoin', tf='30m'):
    relp = True
    BASE_DIR = '/root/trader_webapp'
    rel_path = 'TA-Lib Signals/{}/{}/'.format(market, tf)
    abs_dir = os.path.join(BASE_DIR, rel_path)
    if (relp):
        abs_dir = rel_path
    paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
    for path in paths:
        df = pd.read_csv(path)
        indicator_bb = bb(close=df['close'], window=20,
                          window_dev=2, fillna=False)
        df['upperband'] = indicator_bb.bollinger_hband()
        df['middleband'] = indicator_bb.bollinger_mavg()
        df['lowerband'] = indicator_bb.bollinger_lband()
        df.to_csv(path, header=True, index=True, sep=',', mode='w')
# MakeBollingerBandsSignals()
