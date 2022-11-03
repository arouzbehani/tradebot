import csv
import datetime
from distutils.command.config import config
import math
from pathlib import Path
import ccxt
from matplotlib import pyplot as plt
import numpy as np
import ta
import pandas as pd
from PF import Columns, ColumnsV2
from PF2 import Columns2
import config
from ta.volatility import BollingerBands, AverageTrueRange
import statistics
import test
import scipy.optimize as optimize
import pivot as piv
exchange = ccxt.kucoin({
    'apikey': config.Kucoin_API_Key,
    'secret': config.kucoin_API_Secret
})


def b_size(price):
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

    if price <= 0.25:
        return price/10

    if price > 0.25 and price <= 1:
        return 0.125
    if price > 1 and price <= 3:
        return 0.2
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


def SaveTestData(t_f, lim):
    markets = exchange.load_markets()
    for m in markets:
        try:

            bars = exchange.fetch_ohlcv(m, limit=lim, timeframe=t_f)
            df = pd.DataFrame(bars, columns=['timestamp',
                                             'open', 'high', 'low', 'close', 'volume'])
            filepath = Path('SAVE/'+t_f+'/'+m.replace('/', '_')+'.csv')
            filepath.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(filepath)
            print('success csv save for ' + m)

        except:
            print('error in fetching ' + m)


def FindSignals(m, cols, bsize):
    gn = 0
    totn = 0
    out_gn = 0
    out_totn = 0
    strd = ''
    onecols = ''
    totenters = ''
    totexits = ''
    ln = len(cols)
    if(cols[ln-1].Type == 'X'):
        if(ln > 2):
            if(cols[ln-1].CurrentBox > cols[ln-3].CurrentBox):

                if (cols[ln-1].CurrentBox - cols[ln-3].CurrentBox <= 1.1*bsize):
                    message = 'XXXX ' + m + ' XXXX seems good to enter today : --> ' + \
                        str(cols[ln-1].High) + ' - ' + str(cols[ln-1].Low) + \
                        ' -- current box: ' + \
                        str(cols[ln-1].CurrentBox) + \
                        ' -- box size: ' + \
                        str(round(bsize, 4))
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
    return[gn, totn, out_gn, out_totn, strd, onecols, totenters, totexits]


def ReadMarket(tf='1d',coin='All', lim=500, savefile=True):

    markets = exchange.load_markets()
    if(coin !='All'):
        simple = [t for t in markets if t == coin]
        markets=simple

    gn = 0
    totn = 0
    out_gn = 0
    out_totn = 0
    strd = ''
    onecols = ''
    entry_onecols = ''
    ferrors = ''
    totenters = ''
    totexits = ''

    for m in markets:
        if m.endswith('/USDT'):
            try:
                bars = exchange.fetch_ohlcv(m, limit=lim, timeframe=tf)
                df = pd.DataFrame(bars, columns=['timestamp',
                                                 'open', 'high', 'low', 'close', 'volume'])
                price_avg = statistics.mean(df['high'].values)
                bsize = b_size(price_avg)
                highs = df['high'].values
                lows = df['low'].values
                closes = df['close'].values
                cols = Columns(bsize, 3, highs, lows, closes)
                res = FindSignals(m, cols, bsize)
                gn += res[0]
                totn += res[1]
                out_gn += res[2]
                out_totn += res[3]
                strd += res[4]
                if(res[5] != ''):
                    if(res[5].startswith('Enter')):
                        entry_onecols += res[5].split('in')[1] 

                onecols += res[5]
                totenters += res[6]
                totexits += res[7]
            except:
                ferrors += m + '\n'
                print('error in fetch ' + m)

    onecols += 'Enetr One Cols ****************************************************************' + '\n'
    onecols += entry_onecols
    if(savefile):
        strd += '****************************************************************' + '\n'
        strd += 'good items for today: ' + str(gn) + '\n'
        strd += totenters + '\n'
        strd += 'total items with positive trend: ' + str(totn) + '\n'
        strd += '-----------------------------------------------------------------' + '\n'
        strd += 'good items exit today: ' + str(out_gn) + '\n'
        strd += totexits + '\n'
        strd += 'total items with negative trend: ' + str(out_totn) + '\n'
        folder = 'output_data/'
        fname = folder + 'market-'+str(datetime.datetime.now()
                                       ).split('.')[0].replace(':', "_") + '.txt'
        f = open(fname, "w")
        f.write(strd)
        f.close()

        fname = folder + 'one columns-' + \
            str(datetime.datetime.now()).split(
                '.')[0].replace(':', "_") + '.txt'
        f = open(fname, "w")
        f.write(onecols)
        f.close()

        fname = folder + 'fetch errors-'+str(datetime.datetime.now()
                                             ).split('.')[0].replace(':', "_") + '.txt'
        f = open(fname, "w")
        f.write(ferrors)
        f.close()

    markets = exchange.load_markets()
    for m in markets:
        if m.endswith('/USDT'):
            try:
                bars = exchange.fetch_ohlcv(
                    m, limit=lim, timeframe=tframe)
                df = pd.DataFrame(bars, columns=['timestamp',
                                                 'open', 'high', 'low', 'close', 'volume'])
                df.to_csv("/SAVE/"+m)
                break
            except:
                print()


def ReadMarketGetColumns(name, tframe, hnum, rnum):
    cols = []
    bsize = 1
    markets = exchange.load_markets()
    simple = [t for t in markets if t == name]
    for m in simple:
        if m.endswith('/USDT'):
            try:
                bars = exchange.fetch_ohlcv(
                    m, limit=hnum+rnum, timeframe=tframe)
                df = pd.DataFrame(bars, columns=['timestamp',
                                                 'open', 'high', 'low', 'close', 'volume'])
                price_avg = statistics.mean(df['high'].values)
                bsize = b_size(price_avg)
                highs = df['high'].values
                lows = df['low'].values
                closes = df['close'].values
                cols = ColumnsV2(bsize, 3, highs, lows, closes)

            except:
                print('error in fetch ' + m)
    return [cols, bsize]


def ReadTest(data, start, end, saveprofit=0, stoploss=0):
    if end == 0:
        end = len(data)
    if end >= len(data):
        end = len(data)-1

    highs = data['high'].tolist()[start:end]
    lows = data['low'].tolist()[start:end]
    closes = data['close'].tolist()[start:end]
    price_avg = statistics.mean(closes)
    bsize = b_size(price_avg)
    bsizes = np.arange(price_avg*1/(1000.0), price_avg*1 /
                       (10.0), 0.00099*price_avg, dtype=float)
    # np.append(bsizes,[b_size(price_avg)])
    tests = []

    for b in bsizes:
        cols = Columns(b, 3, highs, lows, closes)
        res = test.Test(cols, bsize, saveprofit, stoploss)
        tests.append(res[1])

    return [bsizes, tests]




def PerformTest(sample_N, step, tot_samples, symbol, t_f, saveprofit, stoploss):

    maxres = []
    minres = []
    max_bamx = []
    min_bmin = []
    xdata = []
    data = pd.read_csv('Test/'+t_f+'/'+symbol+'.csv')
    for a in range(1, tot_samples-sample_N, step):
        xdata.append(a)
        maxes = []
        mins = []
        b_maxes = []
        b_mins = []
        for x in range(a, a+sample_N):
            testres = ReadTest(data, x, x+sample_N, saveprofit, stoploss)
            mx = max(testres[1])
            max_index = (testres[1]).index(mx)
            b_max = (testres[0])[max_index]
            maxes.append(mx)
            b_maxes.append(b_max)

            mn = min(testres[1])
            min_index = (testres[1]).index(mn)
            b_min = (testres[0])[min_index]
            mins.append(mn)
            b_mins.append(b_min)

        max_max = max(maxes)
        ind_max_max = maxes.index(max_max)
        max_bamx.append(b_maxes[ind_max_max])
        min_min = min(mins)
        ind_min_min = mins.index(min_min)
        min_bmin.append(b_mins[ind_min_min])

        maxres.append(max_max)
        minres.append(min(mins))
        print(str(len(maxres)))

    fig = plt.figure()

    fig.suptitle('Symbol:' + symbol + '-- Time Frame: ' + t_f +
                 '-- samples: ' + str(sample_N) + '-- Step Number: ' + str(step))

    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)
    ax1.plot(xdata, maxres, label='Max profit')
    ax1.plot(xdata, minres, label='Max loss')

    ax1.set_xlabel('range')
    ax1.set_ylabel('Max Profit/loss')
    ax1.legend()

    ax2.plot(xdata, max_bamx, label='B_Size_Max')
    ax2.plot(xdata, min_bmin, label='B_size_Min')
    ax2.set_ylabel('Box Size')
    ax2.set_xlabel('range')
    ax2.legend()

    plt.show()
# PerformTest(168,75,1200,"ADA_USDT",'1h',10,10)


def ReadTest_B(params):
    data, b, start, end, saveprofit, stoploss = params
    cols = Columns(b, 3, data['high'].tolist()[start:end], data['low'].tolist()[
                   start:end], data['close'].tolist()[start:end])
    return test.Test(cols, b, saveprofit, stoploss)
# SaveTestData("1d",2000)

# data = pd.read_csv('Test/1h/ADA_USDT.csv')
# initdata=[data,0.0075,0,168,10,10]
# res=ReadTest_B(initdata)
# print(str(res))
# data = pd.read_csv('Test/1h/ADA_USDT.csv')
# cols = Columns2(0.05, 3, data['high'].tolist(), data['low'].tolist(), data['close'].tolist(),data['timestamp'].tolist())
# print (cols)

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
 
 
# ReadMarket('1h','LUNA/USDT',700)
df = pd.read_csv('SAVE\\1h\\BTC_USDT.csv')

piv.getPivots(df)
