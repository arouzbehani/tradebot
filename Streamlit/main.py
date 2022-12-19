from datetime import datetime
from pathlib import Path
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talibHelper import AllPatterns as alp
from ta.volatility import BollingerBands as bb

Base_DIR = '/root/trader_webapp/'
relp = True


def dt(ts):
    return str(datetime.fromtimestamp(int(ts/1000))).split(' ')[0]


def GetData(tf, symbol, exch):
    df = None
    rel_dir = '../Market Data/{}/{}/'.format(exch, tf, symbol)
    # rel_dir='Market Data/{}/{}/'.format(exch,tf,symbol)
    abs_dir = os.path.join(Base_DIR, rel_dir)
    if (relp):
        abs_dir = rel_dir
    for path in Path(abs_dir).iterdir():
        if (path.name.lower().startswith(symbol.lower())):
            df = pd.read_csv(path)

            break
    return df


st.title('Analayzer')


st.sidebar.write("Choose the Operation")


q = st.experimental_get_query_params()
if (q.__contains__('symbol') and q.__contains__('tf') and q.__contains__('exch')):
    symbol = q['symbol'][0]
    tf = q['tf'][0]
    exch = q['exch'][0]
    df = GetData(tf, symbol, exch)
    if (df.size):
        df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
        res, ndf = alp(df)

        fig_vol = go.Scatter(x=df['time'], y=df['volume'], name='Volume')
        if (res):
            fig_bull = go.Scatter(
                x=ndf['time'], y=ndf['bullish'], name='Bullish Patterns', line=dict(color="green"))
            fig_bear = go.Scatter(
                x=ndf['time'], y=ndf['bearish'], name='Bearish Patterns', line=dict(color="red"))
        fig = make_subplots(
            rows=3, cols=1,
            column_widths=[1],
            row_heights=[0.6, 0.2, 0.20],


            shared_xaxes=True, vertical_spacing=0.01,
        )
        # df['upperband'],df['middleband'],df['lowerband']=tah.BoolingerBands(close= df['close'],timeperiod= 20, nbdevdn= 6, nbdevup= 6, matype=0)
        indicator_bb = bb(close=df['close'], window=20,
                          window_dev=2, fillna=False)
        df['upperband'] = indicator_bb.bollinger_hband()
        df['middleband'] = indicator_bb.bollinger_mavg()
        df['lowerband'] = indicator_bb.bollinger_lband()

        # st.dataframe(pd.DataFrame(data=df,columns=['lowerband','middleband','upperband']))

        fig.add_trace(
            go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['middleband'], name='middle band'), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['upperband'], name='upper band'), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['time'], y=df['lowerband'], name='lower band'), row=1, col=1
        )
        fig.add_trace(
            fig_bull, row=2, col=1
        )
        fig.add_trace(
            fig_bear, row=3, col=1
        )

        fig.update_layout(xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # # fig2.update_xaxes(type='category')
        # st.plotly_chart(fig2,use_container_width=True)
        # st.set_option('deprecation.showPyplotGlobalUse', False)


else:
    st.write('no param')
