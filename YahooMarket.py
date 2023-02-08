import yfinance as yf
import pandas as pd
from datetime import datetime
from datetime import timedelta
import calendar , pytz
import GLOBAL
import os


# data = yf.download(tickers="MSFT", period="1d", interval="1m")
# print (data.tail())
# import requests
# import config

# params = {
#   'access_key': config.MarketStack_Key
# }

# api_result = requests.get('https://api.marketstack.com/v1/tickers/aapl/eod', params)

# api_response = api_result.json()

# for stock_data in api_response['data']:
#       print(stock_data['symbol'])
#       print(stock_data['high'])
#       print(stock_data['date'])
    

# tickers = pd.read_html(
#     'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
# print(tickers.head())
def to_utc(t):
    # dashes=t.split('-')
    # offset=dashes[len(dashes)-1]
    # tupletime=datetime.strptime(t.replace(offset,""),"%Y-%m-%d %H:%M:%S")
    # if(len(dashes)>=3):
    #     utc=tupletime + timedelta(hours=-1*int(offset.split(':')[0]))
    # utc=t+datetime(t.year,t.month,t.day,t.hour,t.minute,t.second, microsecond=0, tzinfo=pytz.timezone('America/New York'))
    utc=t+timedelta(days=datetime.utcoffset(t).days,seconds=datetime.utcoffset(t).seconds)
    ttuple = utc.timetuple()
    itimestamp = calendar.timegm(ttuple)
    return itimestamp*1000

def GetMarkets(local=False):
    rel_path='Market Data/Yahoo/companies.csv'
    df=pd.read_csv(GLOBAL.LOCALIZE(rel_path,local))
    return list(df['Symbol'])


def GetMarketData(markets,period=60, tf='1d' , symbol='All',relp=False):
    marketData = []
    errordata = []
    now=datetime.utcnow() #+ timedelta(hours=-5)
    before=now + timedelta(days=-1*period)

    #markets = exchange.load_markets()
    if (symbol != 'All'):
        simple = [t for t in markets if t == symbol]
        markets = simple
    for m in markets:
        try:
            stock = yf.Ticker(m)
            print(f'Downloading Stock:{stock} -- tf:{tf}')
            hist = stock.history(start=f'{before.year}-{before.month}-{before.day}',end=f'{now.year}-{now.month}-{now.day}',interval=tf)
            hist_df = pd.DataFrame(hist).reset_index()
            hist_df=hist_df[hist_df['Volume']!=0]
            if('Datetime' in hist_df.columns):
                hist_df['timestamp']=hist_df['Datetime'].apply(to_utc)
            elif ('Date' in hist_df.columns):
                hist_df['timestamp']=hist_df['Date'].map(to_utc)

            dict = {'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close',
                    'Volume': 'volume'}
            hist_df.rename(columns=dict,inplace=True)
            
            df = pd.DataFrame(hist_df, columns=['timestamp',
                                                'open', 'high', 'low', 'close', 'volume'])
            df["Symbol"] = m
            rel_path='Market Data/Yahoo/{}/{}__{}.csv'.format(tf,m.replace('/','_'),tf)
            abs_path = os.path.join(GLOBAL.BASE(relp), rel_path)
            if(relp):
                abs_path=rel_path
            if(os.path.isfile(abs_path)):
                df0=pd.read_csv(abs_path)
                # fdf=pd.concat([df[:-1],df0]).drop_duplicates().sort_values(by=['timestamp'])
                fdf=pd.concat([df,df0]).drop_duplicates().sort_values(by=['timestamp'])
                fdf.to_csv(abs_path, header=True, index=False, sep=',', mode='w')
            else:
                #fdf=df[:-1]
                fdf=df
                fdf.to_csv(abs_path, header=True, index=False, sep=',', mode='w')
                
            marketData.append(df)

        except:
            print('error in fetching market data for: ' + m + ' --- tf:'+tf)
            errordata.append(m + ':' + tf)
    return (marketData, errordata)

# data = yf.download('MSFT',start='2023-01-01',end='2023-01-21', interval='30m')
# print(data.tail(20))


# df=pd.read_csv('market data/yahoo/15m/aapl_15m.csv')
# df=df[df['Volume']!=0]
# df['timestamp']=df['Datetime'].map(to_utc)
# l=GetMarkets(True).__str__().replace(',','').replace("'",'')
# data = yf.download('GH',period='60d', interval='1d')
# print(data)
# data.to_csv('all_stocks_1m.csv', header=True, index=False, sep=',', mode='w')

#GetMarketData(GetMarkets(True),period=30,tf='30m',symbol='WRB',relp=True)