import os
from pathlib import Path
import signaler as sg
from IPython.display import HTML
import pandas as pd
from ta.volatility import BollingerBands as bb
import pandas as pd
def GetData():
    data = {'1h':[], '1d':[] , '30m':[],'4h':[]}
    for tf in data:
        res , df=sg.TALibPattenrSignals(7*24*60,[tf])
        if( res ==True):
            data[tf].append(df)
            print("{} done!".format(tf))

    return data

def talib():
    data = GetData()
    if (len(data) > 0):
        tables = {'1h': [],
                    '4h': [],
                    '30m': [],
                    '1d': []}
        for d in data:
            if(len(data[d])>0):
                pretty_bullish = data[d][0][[
                    'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
                pretty_bearish = data[d][0][[
                    'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
                tables[d].append(HTML(pretty_bullish.to_html(classes='table table-hovered')))
                tables[d].append(HTML(pretty_bearish.to_html(classes='table table-hovered')))
    print(tables)
def getMarketData(exch='kucoin',coin='BTC_USDT',tf='1h'):
    rel_path = 'Market Data/{}/{}/{}__{}.csv'.format(exch,tf,coin,tf)
    return pd.read_csv(rel_path)


def GetData0():
    BASE_DIR = '/root/trader_webapp'
    data = {'1h':[], '1d':[] , '30m':[],'4h':[]}
    for tf in data:
        rel_path = 'TA-Lib Signals/'+tf+'/'
        abs_dir = os.path.join(BASE_DIR, rel_path)
        abs_dir=rel_path
        paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
        for path in paths:
            df = pd.read_csv(path)
            data[tf].append(df)
    return data

def signals():
    data = GetData0()
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        tables = {'1h': [],
                    '4h': [],
                    '30m': [],
                    '1d': []}
        for d in data:
            if(data[d]):
                pretty_bullish = data[d][len(data[d])-1][[
                    'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
                pretty_bearish = data[d][len(data[d])-1][[
                    'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
                tables[d].append(HTML(pretty_bullish.to_html(classes='table table-hovered')))
                tables[d].append(HTML(pretty_bearish.to_html(classes='table table-hovered')))

    print(tables)

def arraytest():
    l=[1,2,3,4,5,6,7,8,9,10]
    print(f"list -->{l}")
    print(f"l[:-1] -->{l[:-1]}")
    print(f"l[-1:] -->{l[-1:]}")
    print(f"l[-2:-1] -->{l[-2:-1]}")
    print(f"l[-1] -->{l[-1]}")
def BollingerView():
    df=getMarketData(coin='BTC_USDT')
    
    indicator_bb = bb(close=df['close'], window=20,
            window_dev=2, fillna=False)
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['upperband'] = indicator_bb.bollinger_hband()
    df['middleband'] = indicator_bb.bollinger_mavg()
    df['lowerband'] = indicator_bb.bollinger_lband()
    df['pband'] = indicator_bb.bollinger_pband()
    pd.set_option('display.max_rows', 1000)

    print(pd.DataFrame(df , columns=['date','pband']))
#BollingerView()
def arrayshow():
    list=[1,2,3,4,5,6,7,8,9,10]
    print(list[:len(list)-3])
arrayshow()