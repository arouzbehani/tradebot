import bot
import plotter


class Transaction(object):
    def __init__(self):
        self._Index = 0
        self._Price = 0.0
        self._Sell = 0
        self._Buy = 0
        self._ColumnNumber = 0

    @property
    def ColumnNumber(self):
        return self._ColumnNumber

    @ColumnNumber.setter
    def ColumnNumber(self, value):
        self._ColumnNumber = value

    @property
    def Index(self):
        return self._Index

    @Index.setter
    def Index(self, value):
        self._Index = value

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, value):
        self._Price = value

    @property
    def Sell(self):
        return self._Sell

    @Sell.setter
    def Sell(self, value):
        self._Sell = value

    @property
    def Buy(self):
        return self._Buy

    @Buy.setter
    def Buy(self, value):
        self._Buy = value


def btest(name, tframe, hnum, rnum, saveprofit, stoploss):
    profit=0
    money = 100
    token = 0
    transactions = []
    trans = True
    [cols, bsize] = bot.ReadMarketGetColumns(name, tframe, hnum, rnum)
    for x in range(2, len(cols)):
        ln = len(cols)
        if(token > 0):
            if(cols[x].Close*token >= (1 + saveprofit/100)*100):
                t = Transaction()
                t.Sell = cols[x].Close*token
                t.Price = cols[x].Close
                t.ColumnNumber = x+1
                transactions.append(t)
                profit = token*cols[x].Close - 100
                break
            if(cols[x].Close*token >= (1 + stoploss/100)*100):
                t = Transaction()
                t.Sell = cols[x].Close*token
                t.Price = cols[x].Close
                t.ColumnNumber = x+1
                transactions.append(t)
                profit = token*cols[x].Close - 100
                break
        if(cols[x].Type == 'X'):
            if(cols[x].CurrentBox > cols[x-2].CurrentBox):
                if (cols[x].CurrentBox - cols[x].CurrentBox <= 1.0*bsize):
                    if(money > 0 and cols[x].Boxes[-1].Index > hnum):
                        t = Transaction()
                        t.Buy = money
                        t.Price = cols[x].Close
                        t.ColumnNumber = x+1
                        transactions.append(t)
                        trans = True
                        token = money/cols[x].Close
                        money = 0
        else:
            if(cols[x].CurrentBox < cols[x-2].CurrentBox):
                if (cols[ln-3].CurrentBox - cols[ln-1].CurrentBox <= 1.0*bsize):
                    if(token > 0 and cols[ln-3].Boxes[-1].Index > hnum):
                        trans = True
                        money = token*cols[x].Close
                        token = 0
                        t = Transaction()
                        t.Sell = money
                        t.Price = cols[x].Close
                        t.ColumnNumber = x+1
                        transactions.append(t)

                        if(saveprofit > 0 and money/100 >= 1 + saveprofit/100):
                            break
                        if(stoploss > 0 and money/100 <= 1 - stoploss/100):
                            break

    if(profit == 0):
        if(trans):
            if (money == 0 and token > 0):
                profit = token*cols[len(cols)-1].Close - 100
            elif (money > 0 and token == 0):
                profit = money - 100
    print(profit)
    for i in range(0, len(transactions)):
        if(transactions[i].Buy > 0):
            print("Buy:" + str(transactions[i].Buy))
        if(transactions[i].Sell > 0):
            print("Sell:" + str(transactions[i].Sell))
        print("Price:" + str(transactions[i].Price))
        print("Column:" + str(transactions[i].ColumnNumber))

    plotter.GetPlot(cols)


btest("BTC/USDT", "1h", 168, 80, 10, 10)
btest("BTC/USDT", "1h", 168, 168, 10, 10)
