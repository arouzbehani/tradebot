import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime
import streamlit as st
import helper , pivot_helper
import plotly.graph_objects as go
from plotly.subplots import make_subplots



st.set_option('deprecation.showPyplotGlobalUse', False)

with st.sidebar:
    left_candles = st.number_input("Left Candles:", value=3)
    right_candles = st.number_input("Right Candles", value=3)
    data_limit=st.number_input("Data Limit:",value=300)

q = st.experimental_get_query_params()
coin = 'BTC_USDT'
tf = '1d'
if (q.__contains__('symbol')):
    coin = q['symbol'][0]
if (q.__contains__('tf')):
    tf = q['tf'][0]
exch = 'Kucoin'
df = helper.GetData(tf, coin, exch)
df=pd.DataFrame(data=df[-data_limit :]).reset_index(drop=True)
df,up_points,down_points,sidepoints,power_ups,power_downs=pivot_helper.find_pivots(df,left_candles,right_candles,3)



fig = go.Figure(data=go.Candlestick(
    x=df.index, open=df['open'], close=df['close'], high=df['high'], low=df['low']))
fig.add_scatter(x=df.index, y=up_points, mode="markers", marker=dict(
    size=5, color="green"), name='up trend')
fig.add_scatter(x=df.index, y=sidepoints, mode="markers", marker=dict(
    size=5, color="gray"), name='side trend')
fig.add_scatter(x=df.index, y=down_points, mode="markers", marker=dict(
    size=5, color="red"), name='down trend')

fig.add_scatter(x=df.index, y=power_ups, mode="markers", marker=dict(
    size=8, color="green" , symbol='star'), name='stronging up')
fig.add_scatter(x=df.index, y=power_downs, mode="markers", marker=dict(
    size=5, color="red" , symbol='star'), name='stronging down')        
st.plotly_chart(fig, use_container_width=True)
