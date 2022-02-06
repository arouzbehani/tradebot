import datetime
from distutils.command.config import config
import math
import ccxt
import ta
import pandas as pd
from PF import Columns
import config
from ta.volatility import BollingerBands, AverageTrueRange
import statistics

###
#    Price Range	            Box Size
#     Under 0.25	    -->     0.0625
#     0.25 to 1.00      -->  	0.125
#     1.00 to 5.00      -->		0.25
#     5.00 to 20.00	    -->	    0.50
#     20.00 to 100	    -->	    1.00
#     100 to 200	    -->	    2.00
#     200 to 500	    --> 	4.00
#     500 to 1,000      -->		5.00
#     1,000 to 25,000   -->	    50.00
#     25,000 and up     -->     500.00


def b_size(price):

    if price <= 0.25:
        return price/10

    if price > 0.25 and price <= 1:
        return 0.075
    if price > 1 and price <= 3:
        return 0.15
    if price > 3 and price <= 5:
        return 0.25

    if price > 5 and price <= 20:
        return 0.5
    if price > 20 and price <= 100:
        return 1
    if price > 100 and price <= 200:
        return 2
    if price > 200 and price <= 500:
        return 4
    if price > 500 and price <= 1000:
        return 5
    if price > 1000 and price <= 10000:
        return 50
    if price > 10000 and price <= 25000:
        return 0.200
    else:
        return 500


exchange = ccxt.kucoin({
    'apikey': config.Kucoin_API_Key,
    'secret': config.kucoin_API_Secret
})
markets = exchange.load_markets()

gn = 0
totn = 0
out_gn = 0
out_totn = 0
strd = ''
onecols = ''
ferrors = ''
totenters = ''
totexits = ''

for m in markets:
    if m.endswith('/USDT'):
        try:
            bars = exchange.fetch_ohlcv(m, limit=100, timeframe='1d')
            df = pd.DataFrame(bars, columns=['timestamp',
                                             'open', 'high', 'low', 'close', 'volume'])
            price_avg = statistics.mean(df['high'].values)
            bsize = b_size(price_avg)
            highs = df['high'].values
            lows = df['low'].values
            cols = Columns(bsize, 3, highs, lows)
            ln = len(cols)
            if(cols[ln-1].Type == 'X'):
                if(ln > 2):
                    if(cols[ln-1].CurrentBox > cols[ln-3].CurrentBox):

                        if (cols[ln-1].CurrentBox - cols[ln-3].CurrentBox <= 1.1*bsize):
                            message = 'XXXX ' + m + ' XXXX seems good to enter today : --> ' + \
                                str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low) + \
                                ' -- current box: ' + \
                                str(cols[ln-1].CurrentBox) + \
                                ' -- box size: ' + str(math.round(bsize,4))
                            strd += message + '\n'
                            print(message)
                            gn += 1
                            totenters += m + '\n'
                        else:
                            message = 'X --> ' + m + ' has positive trend : ' + \
                                str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low) + \
                                ' -- current box: ' + \
                                str(cols[ln-1].CurrentBox) + \
                                ' -- box size: ' + str(bsize)
                            strd += message + '\n'
                            print(message)
                        totn += 1
                else:
                    message = 'Enter Startegy - One Column in ' + m
                    onecols += message + '\n'
            else:
                if(ln > 2):
                    if(cols[ln-1].CurrentBox < cols[ln-3].CurrentBox):

                        if (cols[ln-3].CurrentBox - cols[ln-1].CurrentBox <= 1.1*bsize):
                            message = 'OOOO ' + m + ' OOOO seems good to exit today : --> ' + \
                                str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low) + \
                                ' -- current box: ' + \
                                str(cols[ln-1].CurrentBox) + \
                                ' -- box size: ' + str(bsize)
                            strd += message + '\n'
                            print(message)
                            out_gn += 1
                            totexits += m + '\n'
                        else:
                            message = 'O --> ' + m + ' has negative trend : ' + \
                                str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low) + \
                                ' -- current box: ' + \
                                str(cols[ln-1].CurrentBox) + \
                                ' -- box size: ' + str(bsize)
                            strd += message + '\n'
                            print(message)
                        out_totn += 1
                else:
                    message = 'Exit Startegy One Column in ' + m + ' box size: ' + \
                        str(bsize) + ' high/lows:--> ' + \
                        str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low)
                    onecols += message + '\n'

        except:
            ferrors += m + '\n'
            print('error in fetch ' + m)


strd += '****************************************************************' + '\n'
strd += 'good items for today: ' + str(gn) + '\n'
strd += totenters + '\n'
strd += 'total items with positive trend: ' + str(totn) + '\n'
strd += '-----------------------------------------------------------------' + '\n'
strd += 'good items exit today: ' + str(out_gn) + '\n'
strd += totexits + '\n'
strd += 'total items with negative trend: ' + str(out_totn) + '\n'

fname = 'market-'+str(datetime.datetime.now()
                      ).split('.')[0].replace(':', "_") + '.txt'
f = open(fname, "w")
f.write(strd)
f.close()

fname = 'one columns-' + str(datetime.datetime.now()
                             ).split('.')[0].replace(':', "_") + '.txt'
f = open(fname, "w")
f.write(onecols)
f.close()

fname = 'fetch errors-'+str(datetime.datetime.now()
                            ).split('.')[0].replace(':', "_") + '.txt'
f = open(fname, "w")
f.write(ferrors)
f.close()


# highs=(df['high']).values
# print(highs)
# print(highs[2])
# # for bar in bars:
# #     print(bar)
# # print (len(bars))
# bb_indicator = BollingerBands(
#     df['close'], window=20, window_dev=2, fillna=True)
# df['upper_band'] = bb_indicator.bollinger_hband()
# df['lower_band'] = bb_indicator.bollinger_lband()
# df['movingaverage']=bb_indicator.bollinger_mavg()
# print(df)

# print(len(cols))
# for x in range(0, len(cols)):
#     print(cols[x].CurrentBox)
#     for i in range(0, len(cols[x].Boxes)):
#         print(cols[x].Boxes[i])
