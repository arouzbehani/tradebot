import pandas as pd
import numpy as np
from sklearn import preprocessing , model_selection , svm
from sklearn.linear_model import LinearRegression
import helper , math , datetime
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot')
tf='30m'
coin='AXS3L_USDT'
df0=helper.GetData(tf=tf,symbol=coin,exch='Kucoin')
helper.append_rsi(df=df0,entry_signal=True,entry_signal_mode='All')
helper.append_fi(df=df0)
helper.append_adx(df=df0)
helper.append_bb(df=df0,entry_signal=True,entry_signal_mode='All')
helper.append_sma(df=df0,entry_signal=True,entry_signal_mode='All')
helper.append_ema(df=df0,entry_signal=True,entry_signal_mode='All')
unixdict={'30m':1800,'1h':3600,'4h':14400,'1d':86400}
# df0=df0[-1200:]
forecast_out=30

df=df0[:-forecast_out]
#df=df[['time','close','open','high','low','volume']]
df['hl_pct']=(df['high']-df['low'])/df['low'] * 100
df['pct_change']=(df['close']-df['open'])/df['low'] * 100
df=df[['time','close','volume','hl_pct','pct_change','rsi_entry_signal','pband','fi_norm','adx_pos_neg']]
forecast_col='close'
df.fillna(-99999,inplace=True)

#forecast_out=int(math.ceil(0.015*len(df)))
print(forecast_out)

df['label']=df[forecast_col].shift(-forecast_out)

X=np.array(df.drop(['time','label'],1))
X=preprocessing.scale(X)
X=X[:-forecast_out]
X_lately=X[-forecast_out:]

df.dropna(inplace=True)

y=np.array(df['label'])
print(10*'*')
X_train,X_test,y_train,y_test=model_selection.train_test_split(X,y,test_size=0.2)
clf=LinearRegression()
clf.fit(X_train,y_train)
accuracy=clf.score(X_test,y_test)

forecast_set=clf.predict(X_lately)
real_set=np.array(df0['close'][-forecast_out:])

print(forecast_set)
print(real_set)
print((real_set-forecast_set)/real_set*100)

print(accuracy)
df['forecast']=np.nan
last_time=df.iloc[-1].time
last_unix=last_time.timestamp()
one_tf=unixdict[tf]
next_unix=last_unix+one_tf

for price in forecast_set:
    next_timestamp=datetime.datetime.fromtimestamp(next_unix)
    next_unix +=one_tf
    df.loc[next_timestamp]=[np.nan for _ in range(len(df.columns)-1)] + [price]

df['close'].plot()
df0['close'].plot()
df['forecast'].plot()
plt.xlabel='Date'
plt.ylabel='Price'
plt.show()

