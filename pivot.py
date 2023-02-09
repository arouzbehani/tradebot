
import numpy as np

import pandas as pd
from scipy.signal import argrelextrema
import scipy.signal as sig
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime

def getPivots(df):
    pivs=[]
    highs = df['high'].values
    lows = df['low'].values
    closes = df['close'].values
    opens = df['open'].values

    peaks=[]
    # print(len(peaks[0]))
    # plt.plot(highs)
    # plt.plot(lows)
    markers=['x','*','.',',','o','X','+','p']
    colors=['r','g','b','c','m','y','k','w']
    for x in range(1,2,2 ):
        peaks=sig.find_peaks(highs,height=1, prominence=2,  distance=2, width=7, threshold=1)[0]
        minima_ind = argrelextrema(lows, np.less,order=1,mode='wrap')[0]

        plt.plot(peaks, highs[peaks], marker=markers[int((x-1)/2)],mfc=colors[int((x-1)/2)])
        plt.plot(minima_ind, lows[minima_ind], marker=markers[int((x-1)/2)],mfc=colors[int((x-1)/2)])


    plt.show()

    
    return [[0,0]]

def dt(ts):
    return str(datetime.fromtimestamp(int(ts/1000))).split(' ')[0]
def FindNears(data,val,p=0.1):
    n=0
    for i in range(0,len(data)):
        if(float(data[i])*(1-p)<= val and val <= float(data[i])*(1+p)):
            n +=1
    if (n ==0 ):
        return 1
    else:
        return n
def FindNears2(data,val,p=0.1):
    nears=[]
    maxv=0
    minv=0
    for i in range(0,len(data)):
        if(float(data[i])*(1-p)<= val):
            if(minv<=data[i]): minv=data[i]
        if(val <= float(data[i])*(1+p)):
            if(maxv>=data[i]): maxv=data[i]

    nears.append(minv)
    nears.append(maxv)
    return nears


class Point(object):
    def __init__(self):
        self._X=None
        self._Y=None
        self._I=None
        self._Date=None
        self._Value=None

    @property
    def X(self):
        return self._X
    @X.setter
    def X(self, value):
        self._X = value
    @property
    def Y(self):
        return self._Y
    @Y.setter
    def Y(self, value):
        self._Y = value        
    @property
    def I(self):
        return self._I
    @I.setter
    def I(self, value):
        self._I = value      
    @property
    def Date(self):
        return self._Date
    @Date.setter
    def Date(self, value):
        self._Date = value
    @property
    def Value(self):
        return self._Value
    @Value.setter
    def Value(self, value):
        self._Value = value      
class Line(object):
    def __init__(self):
        self._P1 = None
        self._P2 = None
    @property
    def P1(self):
        return self._P1
    @P1.setter
    def P1(self, value):
        self._P1 = value
    @property
    def P2(self):
        return self._P2
    @P2.setter
    def P2(self, value):
        self._P2 = value
    def Slope(self):
        return (self._P2.Y-self._P1.Y)/(self._P2.X-self._P1.X)

def MakeWaves(peaks,minima,wavelines,p,loc='minima'):
        points=list(filter(lambda x: (x.X> p.X), peaks))
        nextloc='peaks'
        if(loc=='peaks'):
            points=list(filter(lambda x: (x.X> p.X), minima)) 
            nextloc='minima'
        else:
            nextloc='peaks'
        n=0
        if (len(points)>1):
            line1=Line()
            p1=Point()
            p1.X=points[0].X
            p1.Y=points[0].Y
            p1.I=points[0].I
            p1.Date=points[0].Date
            p1.Value=points[0].Value

            line1.P1=p
            line1.P2=p1
            slope1=line1.Slope()

            line2=Line()
            p2=Point()
            p2.X=points[1].X
            p2.Y=points[1].Y
            p2.I=points[1].I
            p2.Date=points[1].Date
            p2.Value=points[1].Value
            line2.P1=p
            line2.P2=p2
            slope2=line2.Slope()
            nextp=Point()
            if(abs(slope2/slope1)>=1):
                wavelines.append(line2)
                nextp=p2
            else:
                wavelines.append(line1)
                nextp=p1
            MakeWaves(peaks,minima,wavelines,nextp,nextloc)
        else:
            if(len(points)==1):
                line1=Line()
                p1=Point()
                p1.X=points[0].X
                p1.Y=points[0].Y
                p1.I=points[0].I
                p1.Date=points[0].Date
                p1.Value=points[0].Value
                line1.P1=p
                line1.P2=p1
                wavelines.append(line1)
            return
            

def trympf(data,window=2):
    highs=data['High']
    lows=data['Low']
    dates=data['Date']
    markers=['x','*','.',',','o','X','+','p']
    colors=['r','g','b','c','m','y','k','w']

    peaks=sig.find_peaks(highs,height=10, prominence=10,  distance=window, width=2, threshold=3)[0]
    minima_ind = argrelextrema(np.array(lows), np.less,order=3,mode='clip')[0]

    peakpoints=[]
    minimapoints=[]
    for i in range(0,len(peaks)):
        p=Point()
        p.X=peaks[i]
        p.Y=highs[peaks[i]]
        p.I=i
        p.Date=dates[peaks[i]]
        p.Value=highs[peaks[i]]
        peakpoints.append(p)
    for i in range(0,len(minima_ind)):
        p=Point()
        p.X=minima_ind[i]
        p.Y=lows[minima_ind[i]]
        p.I=i
        p.Date=dates[minima_ind[i]]
        p.Value=lows[minima_ind[i]]
        minimapoints.append(p)

    wavelines=[]
    MakeWaves(peakpoints,minimapoints,wavelines,minimapoints[0])
    wavesdata=[]
    for i in range( 0 , len(wavelines)):
        wavesdata.append((wavelines[i].P1.Date,float(wavelines[i].P1.Value)))
    wavesdata.append((wavelines[-1].P2.Date,float(wavelines[-1].P2.Value)))
    peakslines=[]
    minimalines=[]
    rslines=[]
    supports=[]
    resistances=[]
    near_high=[]
    near_low=[]
    thicknesses=[]
    scolors=[]
    rcolors=[]

    for i in range(0,len(peaks)):
        resistances.append(float(highs[peaks[i]]))
        resistances +=FindNears2(highs,float(highs[peaks[i]]),0.025)
        near_high.append(FindNears(highs,float(highs[peaks[i]]),0.15))
        peakslines.append((dates[peaks[i]],float(highs[peaks[i]])))
    for i in range(0,len(minima_ind)):
        supports.append(float(lows[minima_ind[i]]))
        supports +=FindNears2(lows,float(lows[minima_ind[i]]),0.025)
        near_low.append(FindNears(lows,float(lows[minima_ind[i]]),0.15))
        minimalines.append((dates[minima_ind[i]],float(lows[minima_ind[i]])))
    rslines=resistances+supports
    thicknesses = near_low + near_high
    rcolors=['r']*len(resistances)
    scolors=['g']*len(supports)
    thicknesses2 = [0.8]*len(rslines)
    normalized_thick = [element*5 / max(thicknesses) for element in thicknesses]

    mpf.plot(data,type='candle',style='yahoo',alines=dict(alines=[minimalines,peakslines,wavesdata],colors=['r','g','b'],linewidths=[0.5,0.5,1]) , hlines=dict(hlines=rslines,linewidths=thicknesses2 , alpha=0.35 ,colors=rcolors+scolors))
    mpf.show()

rel_path = 'Market Data/{}/{}/{}__{}.csv'.format('Kucoin','1d','BTC_USDT','1d')
df= pd.read_csv(rel_path)
arr=np.array(df['timestamp'].values)
arr = np.array(list(map(dt, arr)))
data = {'Date': arr, 'Open': df['open'].values,'Close':df['close'].values,'High':df['high'].values,'Low':df['low'].values}
ndf=pd.DataFrame(data)
ndf.index=pd.DatetimeIndex(ndf['Date'])
trympf(ndf[-500:],window=20)
# getPivots(df)