import situations as s
import streamlit as st
import helper , Constants as c
import pivot_helper
import analyzer as a 
# from statistics import mean
# import plotly.graph_objects as go
# import numpy as np
# import pandas as pd
# from talibHelper import AllPatterns as alp
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import r2_score
# from sklearn import preprocessing, model_selection, svm
# from plotly.subplots import make_subplots
# import matplotlib.pyplot as plt
# from matplotlib import style
# import datetime
# import plotly.figure_factory as ff
# import MarketReader as mr

def getTilte():
    q = st.experimental_get_query_params()
    if (q.__contains__('symbol')):
        return f'{q["symbol"][0]} Analysis'
    return "Analysis"


st. set_page_config(layout="wide", page_title=getTilte())
st.markdown("""

        <style>
                ..css-k1ih3n {
                    padding: 0;
                }

        </style>
        """, unsafe_allow_html=True)

# symbol = 'MATIC_USDT'
# exch = 'Kucoin'
# symbol = None
# exch = None
q = st.experimental_get_query_params()
if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
if (q.__contains__('exch')):
    exch = q['exch'][0]
if (symbol != None):
    st.title(symbol.replace('_', '-').upper())
    url = 'https://kucoin.com/trade/{}'.format(
        symbol.replace('_', '-').upper())
    link = (st.markdown(f'''
    <a href={url}><button style="background-color:transparent;border:none;text-decoration: underline; color:#21a58a; font-size:large">View {symbol.replace('_','/')} Chart on Kucoin</button></a>
''',
                        unsafe_allow_html=True))

st.sidebar.title("Analysis Settings: ")

with st.sidebar:
    analysis = st.selectbox('Analysis Version', ['1.0'])
    if analysis == '1.0':
        trend_limit_long = st.number_input(
            "Long Term Trend Limit:", min_value=70, value=280)
        trend_limit_short = st.number_input(
            "Short Term Trend Limit:", min_value=20, value=80)
        st.write("1d Pivot Settings:")
        long_term_pivot_candles = st.number_input(
            "Long Term Candles:", min_value=2, value=16)
        short_term_pivot_candles = st.number_input(
            "Short Term Candles:", min_value=2, value=6)
        pvt_trend_number = st.number_input(
            "Pivot Trend Number:", min_value=2, value=2)
        
        waves_number = st.number_input(
            "PA Power Calc. Waves:", min_value=2, value=2)
        sr_limit = st.number_input("S/R Limit:", min_value=70, value=120)

analyzer=a.Analyzer()
analyzer.init_data(exch=exch,symbol=symbol,trend_limit_long=trend_limit_long,trend_limit_short=trend_limit_short,long_term_pivot_candles=long_term_pivot_candles,short_term_pivot_candles=short_term_pivot_candles,
                   pvt_trend_number=pvt_trend_number,waves_number=waves_number)
header,op_point,op,thr_point,thr,point=analyzer.report_buy('1h')
st.header(header)
st.write(f"Opportunities with point: {op_point}")
st.write(op)
st.write(f"Threats with point: {thr_point}")
st.write(thr)


      