import datetime
import time
import kucoinMarkets as kc
import talibHelper as tah
import yfinance as yf


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


def FindSignals_01(maxdelay_min):
    kucoinmarkets = []
    # timeframes = ['5m', '15m', '1h', '4h', '1d', '1w']
    timeframes = ['1h']
    errors = []
    markets = []

    for i in range(0, len(timeframes)):
        markets=kc.GetMarkets()
        datframes, e = kc.GetMarketData(markets,timeframes[i], 'All', 350)
        errors.append(e)
        for df in datframes:

            md = MarketData()
            if (len(df['Coin']) > 0):
                md.Coin = df['Coin'][0]
            else:
                md.Coin = 'ND'
            md.TimeFrame = timeframes[i]
            
            try:
                res , md.Data = tah.MorningStars(df)
                if(res):
                    kucoinmarkets.append(md)
            except:
                print('Error in finding signal : '+md.TimeFrame + "___"+md.Coin)
           # md.Data = df
    

    for kmd in kucoinmarkets:
        if(len(kmd.Data)>0):
            
            now=datetime.datetime.now()
            now_timestamp = time.time() - maxdelay_min*60
            dt_string ="Scan Report/"+kmd.TimeFrame+"___"+kmd.Coin.replace('/','_')+"_"+ now.strftime("%d%m%Y%H%M%S")+".txt"
            try:
                filtered_df = kmd.Data.loc[(kmd.Data['timestamp'] >= now_timestamp*1000)]
                if(len(filtered_df)>0):
                    filtered_df.to_csv(dt_string, header=True, index=True, sep=' ', mode='w')
            except:
                print('Not able to write to file')



# data = yf.download("SPY", start="2022-05-01", end="2022-11-30")
# print(data)
# utcnow=datetime.datetime.now(datetime.timezone.utc)
# print(utcnow)
# print(time.time())

FindSignals_01(4*60)