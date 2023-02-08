import pandas as pd

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
        transaction.Buy_time=self.buys[-1][1]
        transaction.Buy_price=self.buys[-1][2]
        transaction.Coin=self.buys[-1][0]
        transaction.Sell_time=time
        transaction.Sell_price=sell_price
        transaction.Profit=100*round((transaction.Sell_price - transaction.Buy_price) / transaction.Buy_price* self.trading_fee_multiplier,2)
        transaction.Balance_amount=self.balance_amount
        self.transactions.append(transaction)
    def dataframe(self):
        fields = ['Buy_time','Buy_price', 'Sell_time', 'Sell_price','Profit','Balance_amount','Signal_time']
        return pd.DataFrame([{fn: getattr(f, fn) for fn in fields} for f in self.transactions])

