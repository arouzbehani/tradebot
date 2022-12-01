from datetime import datetime
import talib
import pandas as pd


def dt(ts):
    return str(datetime.fromtimestamp(int(ts/1000)))


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
