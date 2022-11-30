from datetime import datetime
import talib
import kucoinMarkets as kc
def dt(ts):
    return str(datetime.fromtimestamp(int(ts/1000)))

km_1d = kc.GetMarketData('1h', 'FTM/USDT', 350)
km_5m = kc.GetMarketData('1h', 'FTM/USDT', 350)
def ReturnMorningStars(data):
    

for d in km_1d:
    morning_starts = talib.CDLMORNINGSTAR(
        d['open'], d['high'], d['low'], d['close'])
    d['Morning Stars']=morning_starts
    d['date time']=d['timestamp'].map(dt)
    signals=morning_starts[morning_starts!=0]
    print(d[d['Morning Stars']!=0])
    
