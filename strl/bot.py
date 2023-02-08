import math
import os
import time
import numpy as np
from datetime import datetime
import pandas as pd
from talibHelper import AllPatterns as alp
from ta.volatility import BollingerBands as bb
from ta.momentum import RSIIndicator as rsi
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize

BASE_DIR='/root/trader_webapp'
relp=True

class Transaction:
    def __init__(self,coin,buy_time,signal_time, buy_price:float):
        self._Coin=coin
        self._Buy_time=buy_time
        self._Buy_price=buy_price
        self._Sell_time=None
        self._Sell_price=0.0
        self._Balance_amount=0.0
        self._Profit=0.0
        self._Signal_time=signal_time

    @property
    def Coin(self):
        return self._Coin
    @Coin.setter
    def Coin(self, value):
        self._Coin = value

    @property
    def Buy_time(self):
        return self._Buy_time
    @Buy_time.setter
    def Buy_time(self, value):
        self._Buy_time = value

    @property
    def Buy_price(self):
        return self._Buy_price
    @Buy_price.setter
    def Buy_price(self, value):
        self._Buy_price = value

    @property
    def Sell_time(self):
        return self._Sell_time
    @Sell_time.setter
    def Sell_time(self,value):
        self._Sell_time=value

    @property
    def Sell_price(self):
        return self._Sell_price
    @Sell_price.setter
    def Sell_price(self,value):
        self._Sell_price=value

    @property
    def Balance_amount(self):
        return self._Balance_amount
    @Balance_amount.setter
    def Balance_amount(self,value):
        self._Balance_amount=value

    @property
    def Profit(self):
        return self._Profit
    @Profit.setter
    def Profit(self,value):
        self._Profit=value

    @property
    def Signal_time(self):
        return self._Signal_time
    @Signal_time.setter
    def Signal_time(self,value):
        self._Signal_time=value  
            

class TradingEnv:
    def __init__(self, balance_amount, balance_unit, trading_fee_multiplier):
        self.balance_amount = balance_amount
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []
        self.transactions=[]
        self.trading_fee_multiplier = trading_fee_multiplier
        
    def buy(self, symbol, buy_price, time):
        self.balance_amount = (self.balance_amount / buy_price) * self.trading_fee_multiplier
        self.balance_unit = symbol
        self.buys.append([symbol, time, buy_price])
        
    def sell(self, sell_price, time,transaction:Transaction):
        self.balance_amount = self.balance_amount * sell_price * self.trading_fee_multiplier
        self.sells.append( [self.balance_unit, time, sell_price] )
        self.balance_unit = 'USDT'
        transaction.Sell_time=time
        transaction.Sell_price=sell_price
        transaction.Profit=100*round((transaction.Sell_price - transaction.Buy_price) / transaction.Buy_price* self.trading_fee_multiplier,2)
        transaction.Balance_amount=self.balance_amount

        #transaction.CalculateProfit()
        self.transactions.append(transaction)

def ComputeData(rawdf):
    
    indicator_bb = bb(close=rawdf['close'], window=20,
                        window_dev=2, fillna=False)

    rawdf['upperband'] = indicator_bb.bollinger_hband()
    rawdf['middleband'] = indicator_bb.bollinger_mavg()
    rawdf['lowerband'] = indicator_bb.bollinger_lband()
    rawdf['bandwidth'] = indicator_bb.bollinger_wband()
    rawdf['pband'] = indicator_bb.bollinger_pband()
    rsi_indicator=rsi(close=rawdf['close'],window=14,fillna=False)
    rawdf['rsi'] = rsi_indicator.rsi()

    
    res,df=alp(rawdf)
    if(res): return df
    return rawdf
csvdf=None
coin=''
# def bollinger_strategy_bot(coin='BTC_USDT',exch='Kucoin',tf='1h', balance_amount=10,balance_unt='USDT',fee=0.99875, stoploss=0.01,profit=0.025):
def bollinger_strategy_bot(x):

    ### x[0] : Profit
    ### x[1] : stopLoss
    tfs={'30m':1,'1h':2,'4h':3,'1d':4}
    profit=x[0]
    stoploss=x[1]

    balance_unt='USDT'
    balance_amount=10
    # stoploss=0.01
    fee=0.99875
    env=TradingEnv(balance_amount=balance_amount,balance_unit=balance_unt,trading_fee_multiplier=fee)
    cdf=ComputeData(csvdf)
    bb_entry_squeez_signals=[]
    bb_exit_squeez_signals=[]
    bb_entry_signals=[]
    bb_exit_signals=[]
    
    df=cdf.loc[cdf['middleband'].isna()==False].reset_index()
    df['date']=pd.to_datetime(df['timestamp'],unit='ms')
    for i in range(1,len(df[:len(df)-10])):

        last_close = df.loc[i,"close"]
        last_lowerband = df.loc[i,'lowerband']
        last_upperband = df.loc[i,'upperband']
        one_to_last_close = df.loc[i-1,'close']
        one_to_last_lowerband = df.loc[i-1,'lowerband']
        one_to_last_upperband = df.loc[i-1,'upperband']
        one_to_last_pband = df.loc[i-1,'pband']

        if (one_to_last_close < one_to_last_lowerband):
            if (last_close > last_lowerband):
                if(df.loc[i,'rsi']<=25):
                    bb_entry_signals.append(df.loc[i])
                    df.loc[i,'bollinger']='BB Entry Signal'
            if (last_close < last_lowerband and one_to_last_pband < 0):
                if(df.loc[i,'rsi']>=70):
                    bb_exit_squeez_signals.append(df.loc[i])
                    df.loc[i,'bollinger']='BB Squeez Exit Signal'

        elif (one_to_last_close > one_to_last_upperband):
            if (last_close > last_upperband and one_to_last_pband >= 1):
                #if(df.loc[i,'rsi']<=25):
                if(True):
                    bb_entry_squeez_signals.append(df.loc[i])
                    df.loc[i,'bollinger']= "BB Squeez Entry Signal"

            if (last_close < last_upperband):
                if(df.loc[i,'rsi']>=75):
                    bb_exit_signals.append(df.loc[i])
                    df.loc[i,'bollinger']= "BB Exit Signal"

    colnames=['timestamp','date','low','high','open','close','bullish','bearish','volume']
    entrydf=pd.DataFrame(bb_entry_signals,columns=colnames).reset_index()
    entry_squeezdf=pd.DataFrame(bb_entry_squeez_signals,columns=colnames).reset_index()
    entry=entrydf
    buying=False
    for i in range(len(entry)):
        forward=df.loc[df['timestamp']>entry.loc[i,'timestamp']].reset_index()
        if(len(env.transactions)>0):
            lastsell=env.transactions[-1].Sell_time
            if(entry.loc[i,'date']<lastsell):continue
        transaction=None
        
        for j in range(0,len(forward)):
            low = forward.loc[j,"low"]
            high = forward.loc[j,"high"]
            open = forward.loc[j,"open"]
            close = forward.loc[j,"close"]
            date = forward.loc[j,"date"]
            bollinger =str(forward.loc[j,"bollinger"])
            if(buying==False):
                env.buy(symbol=coin,buy_price=open,time=date)
                transaction=Transaction(coin=coin,buy_time=date,buy_price=open,signal_time=entry.loc[i,'date'])
                
                buying=True
            if(buying):
                if(high> (1+profit)*env.buys[-1][2]):
                    env.sell((1+profit)*env.buys[-1][2],time=date,transaction=transaction)
                    buying=False
                    break
                if(low< (1-stoploss) * env.buys[-1][2]):
                    env.sell((1-stoploss)*env.buys[-1][2],time=date,transaction=transaction)
                    buying=False
                    break
                if(bollinger.__contains__('Exit')):
                    env.sell(close,time=date,transaction=transaction)
                    buying=False
                    break




    #print(env.balance_amount,env.balance_unit)
    fields = ['Buy_time','Buy_price', 'Sell_time', 'Sell_price','Profit','Balance_amount','Signal_time']
    transdf=pd.DataFrame([{fn: getattr(f, fn) for fn in fields} for f in env.transactions])
    transdf['date']=transdf['Signal_time']
    merged=pd.DataFrame(data= df.merge(transdf, how = 'inner' ,indicator=False),columns=['date','Buy_time','Buy_price','Balance_amount','Profit','bullish','bearish','volume','bollinger','rsi'])
    print(merged)
    if(env.balance_unit=='USDT'):
        return env.balance_amount
    else:
        return 100000


# exch='Kucoin'
# tf='4h'
# coin='BTC_USDT'
# rel_path='Market Data/{}/{}/{}__{}.csv'.format(exch,tf,coin,tf)
# abs_dir = os.path.join(BASE_DIR, rel_path)
# if(relp):
#     abs_dir=rel_path
# csvdf=pd.read_csv(abs_dir)


# def objective(x):
#     return -bollinger_strategy_bot(x)
# def constraint(x):
#     return (x[0] + x[1])
# cons={'type':'ineq','fun':constraint}
# x0=np.array([0.01,0.01])
# sol=minimize(objective,x0,method='SLSQP', bounds=[(0.03,0.5),(0.05,0.1)], options={'disp':True})
# xOpt=sol.x
# balance=-sol.fun
# print(balance)
# print('profit:{} -- stoploss:{}'.format(xOpt[0],xOpt[1]))
# # res=minimize_scalar(bollinger_strategy_bot,bounds=(0.01, 0.09), method='bounded')
# # print(res.x)
# # print(100000-bollinger_strategy_bot(res.x))
# # bollinger_strategy_bot(coin='BTC_USDT',tf='4h', balance_amount=10,profit=0.03,stoploss=0.03)