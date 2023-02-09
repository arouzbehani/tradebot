from datetime import datetime
import talib
import pandas as pd
from patterns import patterns


def dt(ts):
    return str(datetime.fromtimestamp(int(ts/1000)))


def bullish(v):
    if (v > 0):
        return v/100
    return 0


def bearish(v):
    if (v < 0):
        return abs(v)/100
    return 0


def bullish_pat(v, pat):
    if (v > 0):
        return pat+','
    return ''


def bearish_pat(v, pat):
    if (v < 0):
        return pat+','
    return ''


def MorningStars(data):
    try:
        morning_starts = talib.CDLMORNINGSTAR(
            data['open'], data['high'], data['low'], data['close'])
        data['Morning Stars'] = morning_starts
        data['date time'] = data['timestamp'].map(dt)
        return True, (data[data['Morning Stars'] != 0])
    except:
        print('TA-Lib Error in Func: Morning Star')
        return False, []


def AllPatterns(data):
    failedpatterns = []
    data['bullish'] = 0
    data['bearish'] = 0
    data['bullish patterns'] = ''
    data['bearish patterns'] = ''
    for p in patterns:
        try:
            func = getattr(talib, p)
            res = func(data['open'], data['high'], data['low'], data['close'])
            data[p] = res
            data['date time'] = data['timestamp'].map(dt)
            data['bullish'] += data[p].map(bullish)
            data['bearish'] += data[p].map(bearish)
            data['bullish patterns'] += data[p].apply(bullish_pat, pat=p)
            data['bearish patterns'] += data[p].apply(bearish_pat, pat=p)

        except:
            failedpatterns.append(p)
    filterddata = []
    for p in patterns:
        try:
            filtered = (data[data[p] != 0])
            if (filtered.size > 0):
                filterddata.append(filtered)
        except:
            pass
    finalres=pd.concat(filterddata).drop_duplicates().sort_values(by=['timestamp'])

    return True, finalres
def BoolingerBands(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
    
    return talib.BBANDS(close, timeperiod=timeperiod, nbdevup=nbdevup, nbdevdn=nbdevdn, matype=matype)