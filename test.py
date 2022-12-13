import os
from pathlib import Path
import signaler as sg
from IPython.display import HTML
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

l=[1,2,3,4]
print(l[-1])