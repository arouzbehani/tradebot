import pandas as pd

class Transaction:
    def __init__(self,coin,buy_time,signal_time, buy_price:float,trade_mode='spot',sl=0,tp=0):
        self._Coin=coin
        self._Buy_time=buy_time
        self._Buy_price=buy_price
        self._Sell_time=None
        self._Sell_price=0.0
        self._Balance_amount=0.0
        self._Profit=0.0
        self._Signal_time=signal_time
        self._TradeMode=trade_mode
        self._TP=tp
        self._SL=sl

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
            
    @property
    def Trade_Mode(self):
        return self._TradeMode
    @Trade_Mode.setter
    def Trade_Mode(self,value):
        self._TradeMode=value  
    
    @property
    def SL(self):
        return self._SL
    @SL.setter
    def SL(self,value):
        self._SL=value  

    @property
    def TP(self):
        return self._TP
    @TP.setter
    def TP(self,value):
        self._TP=value  
            
class TradingEnv:
    def __init__(self, balance_amount, balance_unit, trading_fee_multiplier,leverage):
        self.balance_amount = balance_amount
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []
        self.wins=0
        self.transactions=[]
        self.trading_fee_multiplier = trading_fee_multiplier
        self.leverage=leverage
        
    def buy(self, symbol, buy_price, time,sl=0,tp=0,trade_mode='spot'):
        self.balance_amount = (self.balance_amount-self.trading_fee_multiplier*buy_price) / buy_price
        self.balance_unit = symbol
        self.buys.append([symbol,trade_mode,time, buy_price, sl,tp])
        
    def sell(self, transaction:Transaction):
        last_buy_price=self.buys[-1][3]
        gain=0
        if (transaction.Trade_Mode=='short'):
            gain=(last_buy_price-transaction.Sell_price)*self.leverage-self.trading_fee_multiplier*transaction.Sell_price
            
        else:
            gain=(transaction.Sell_price-last_buy_price)*self.leverage-self.trading_fee_multiplier*transaction.Sell_price
        
        transaction.Profit=round(100*(gain / (self.balance_amount * last_buy_price)),4)
        self.balance_amount=self.balance_amount * last_buy_price + gain
        transaction.Balance_amount=self.balance_amount
       
        if transaction.Profit>0:
            self.wins +=1

        self.balance_unit = 'USDT'
        transaction.Coin=self.buys[-1][0]
        transaction.Buy_time=self.buys[-1][2]
        transaction.Trade_Mode=self.buys[-1][1]
        transaction.Buy_price=self.buys[-1][3]
        self.sells.append([self.balance_unit, transaction.Trade_Mode, transaction.Sell_time, transaction.Sell_price])

        self.transactions.append(transaction)
        return transaction.Balance_amount
    def dataframe(self):
        fields = ['Buy_time','Trade_Mode','Buy_price', 'Sell_time', 'Sell_price','Profit','Balance_amount','Signal_time']
        return pd.DataFrame([{fn: getattr(f, fn) for fn in fields} for f in self.transactions])
    
