

from tracemalloc import stop
from matplotlib.transforms import Transform


def Test(cols, bsize, saveprofit=0, stoploss=0):
    money = 100
    token = 0
    transaction = False
    for x in range(2, len(cols)):
        ln = len(cols)
        if(cols[x].Type == 'X'):
            if(cols[x].CurrentBox > cols[x-2].CurrentBox):
                if (cols[x].CurrentBox - cols[x].CurrentBox <= 1.0*bsize):
                    if(money > 0):
                        transaction = True
                        token = money/cols[x].Close
                        money = 0
        else:
            if(cols[x].CurrentBox < cols[x-2].CurrentBox):
                if (cols[ln-3].CurrentBox - cols[ln-1].CurrentBox <= 1.0*bsize):
                    if(token > 0):
                        transaction = True
                        money = token*cols[x].Close
                        token = 0
                        if(saveprofit > 0 and money/100 >= 1 + saveprofit/100):
                            break
                        if(stoploss > 0 and money/100 <= 1 - stoploss/100):
                            break

    profit = 0
    if(transaction):
        if (money == 0 and token > 0):
            profit = token*cols[len(cols)-1].Close - 100
        elif (money > 0 and token == 0):
            profit = money - 100

    #return ["Profit: " + str(profit), profit]
    return profit
