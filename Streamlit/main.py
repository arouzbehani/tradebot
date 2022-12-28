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
from ta.momentum import RSIIndicator as rsi
from ta.trend import EMAIndicator as ema
from ta.trend import SMAIndicator as sma

Base_DIR = '/root/trader_webapp/'
relp = True
st. set_page_config(layout="wide")


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


q = st.experimental_get_query_params()

st.title('Analayzer')
if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
    url = 'https://kucoin.com/trade/{}'.format(
        symbol.replace('_', '-').upper())
    st.markdown(f'''
    <a href={url}><button style="background-color:transparent;border:none;text-decoration: underline; color:#21a58a; font-size:large">View {symbol.replace('_','/')} Chart on Kucoin</button></a>
''',
                unsafe_allow_html=True)

st.sidebar.write("Choose the Operation")


def DrawChart(limit=500, read_patterns=False, read_rsi=True, read_bb=True, read_sma=True, read_ema=False, read_vol=True):
    if (q.__contains__('symbol') and q.__contains__('tf') and q.__contains__('exch')):
        symbol = q['symbol'][0]

        read_bull_patterns = read_patterns
        read_bear_patterns = read_patterns
        patterns_res = False
        read_rsi = read_rsi
        read_bb = read_bb
        read_sma = read_sma
        read_ema = read_ema
        read_vol = read_vol

        tf = q['tf'][0]
        exch = q['exch'][0]
        df = GetData(tf, symbol, exch)
        if (df.size):
            limit = limit
            if (len(df) < limit):
                limit = len(df)
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df[-limit:]
            if (read_bull_patterns):
                try:
                    patterns_res, ndf = alp(df)
                except:
                    patterns_res = False

            cond = [read_bull_patterns, read_bear_patterns, read_rsi, read_vol]
            rownum = 1 + len([x for x in cond if x == True])
            row_heights = [0.6]
            for k in range(0, rownum-1):
                row_heights.append(0.4/(rownum-1))
            fig = make_subplots(
                rows=rownum, cols=1,
                column_widths=[1],
                row_heights=row_heights,
                shared_xaxes=True, vertical_spacing=0.01,
            )
            # df['upperband'],df['middleband'],df['lowerband']=tah.BoolingerBands(close= df['close'],timeperiod= 20, nbdevdn= 6, nbdevup= 6, matype=0)

            # st.dataframe(pd.DataFrame(data=df,columns=['lowerband','middleband','upperband']))

            fig.add_trace(
                go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
            )
            rownum = 1
            if (patterns_res):
                rownum += 1
                fig_bull = go.Scatter(
                    x=ndf['time'], y=ndf['bullish'], name='Bullish Patterns', line=dict(color="green"))
                fig_bear = go.Scatter(
                    x=ndf['time'], y=ndf['bearish'], name='Bearish Patterns', line=dict(color="red"))
                fig.add_trace(
                    fig_bull, row=rownum, col=1
                )
                rownum += 1
                fig.add_trace(
                    fig_bear, row=rownum, col=1
                )

            if (read_bb):
                indicator_bb = bb(close=df['close'], window=20,
                                  window_dev=2, fillna=False)
                df['upperband'] = indicator_bb.bollinger_hband()
                df['middleband'] = indicator_bb.bollinger_mavg()
                df['lowerband'] = indicator_bb.bollinger_lband()
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['middleband'], name='middle band'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['upperband'], name='upper band'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['lowerband'], name='lower band'), row=1, col=1
                )
            if (read_rsi):
                rownum += 1
                rsi_indicator = rsi(close=df['close'], window=14, fillna=False)
                df['rsi'] = rsi_indicator.rsi()
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['rsi'], name='rsi'), row=rownum, col=1
                )
            if (read_vol):
                rownum += 1
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['volume'], name='Volume'), row=rownum, col=1
                )
            if (read_sma):
                sma_indicator_5 = sma(
                    close=df['close'], window=5, fillna=False)
                sma_indicator_10 = sma(
                    close=df['close'], window=10, fillna=False)
                sma_indicator_30 = sma(
                    close=df['close'], window=30, fillna=False)
                df['sma_5'] = sma_indicator_5.sma_indicator()
                df['sma_10'] = sma_indicator_10.sma_indicator()
                df['sma_30'] = sma_indicator_30.sma_indicator()
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_5'], name='sma 5'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_10'], name='sma 10'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_30'], name='sma 30'), row=1, col=1
                )
            if (read_ema):
                ema_indicator_5 = ema(
                    close=df['close'], window=5, fillna=False)
                ema_indicator_10 = ema(
                    close=df['close'], window=10, fillna=False)
                ema_indicator_30 = ema(
                    close=df['close'], window=30, fillna=False)
                df['ema_5'] = ema_indicator_5.ema_indicator()
                df['ema_10'] = ema_indicator_10.ema_indicator()
                df['ema_30'] = ema_indicator_30.ema_indicator()
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_5'], name='ema 5'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_10'], name='ema 10'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_30'], name='ema 30'), row=1, col=1
                )

            fig.update_layout(xaxis_rangeslider_visible=False, height=900)
            st.plotly_chart(fig, use_container_width=True)

            # # fig2.update_xaxes(type='category')
            # st.plotly_chart(fig2,use_container_width=True)
            # st.set_option('deprecation.showPyplotGlobalUse', False)

    else:
        st.write('no param')


with st.sidebar:
    limit = st.number_input("Data Limit:", min_value=70, value=300)
    bb_check = st.checkbox("Bollinger bands", value=True)
    rsi_check = st.checkbox("RSI", value=True)
    patterns_check = st.checkbox("Patterns", value=False)
    sma_check = st.checkbox("SMA", value=True)
    ema_check = st.checkbox("EMA", value=False)
    vol_check = st.checkbox("Volume", value=True)


DrawChart(limit=limit, read_vol=vol_check, read_bb=bb_check,
          read_ema=ema_check, read_sma=sma_check,read_patterns=patterns_check,read_rsi=rsi_check)
