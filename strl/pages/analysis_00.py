import situations as s
import streamlit as st
import helper , Constants as c
import pivot_helper
import analyzer as a 
from plotly.subplots import make_subplots
import plotly.graph_objects as go
# from statistics import mean
# import plotly.graph_objects as go
# import numpy as np
import pandas as pd
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

tf='1d'
symbol = 'FTM_USDT'
exch = 'Kucoin'

# symbol = None
# exch = None
q = st.experimental_get_query_params()
if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
if (q.__contains__('exch')):
    exch = q['exch'][0]
if (q.__contains__('tf')):
    tf = q['tf'][0]

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

            
def DrawCandleSticks(df,df2,both=True):
        fig = make_subplots(
        rows=1, cols=1,
        column_widths=[1],
        row_heights=[1],
        shared_xaxes=True, vertical_spacing=0.01)

        if both:

            fig.add_trace(
                go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
            )    
            pointpos_df = pd.DataFrame(
                data=df[~pd.isnull(df['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
            pointpos_df2 = pd.DataFrame(
                data=df2[~pd.isnull(df2['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])

            fig.add_trace(
                go.Scatter(x=pointpos_df['time'], y=pointpos_df['pointpos'], line=dict(
                    color="#3d5ab2"), name='long term wave line')
            )
            fig.add_trace(
                go.Scatter(x=pointpos_df2['time'], y=pointpos_df2['pointpos'], line=dict(
                    color="#9999ff"), name='short term wave line')
            )    
            return fig
        else:
            fig.add_trace(
                go.Candlestick(x=df2['time'], open=df2['open'], close=df2['close'], high=df2['high'], low=df2['low'], name=symbol.replace('_', '/')), row=1, col=1
            )    
            pointpos_df2 = pd.DataFrame(
                data=df2[~pd.isnull(df2['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
            fig.add_trace(
                go.Scatter(x=pointpos_df2['time'], y=pointpos_df2['pointpos'], line=dict(
                    color="#9999ff"), name='short term wave line')
            )    
            return fig



def DoAnalysis():
    #tf='1h'
    analyzer=a.Analyzer()
    analyzer.init_data(tfs=tfs,exch=exch,symbol=symbol,trend_limit_long=trend_limit_long,trend_limit_short=trend_limit_short,long_term_pivot_candles=long_term_pivot_candles,short_term_pivot_candles=short_term_pivot_candles,
                    pvt_trend_number=pvt_trend_number,waves_number=waves_number)
    #sit_1h=s.Situation()
    sit=analyzer.situations[tf]
    header,op_point,op,thr_point,thr,point=analyzer.report_buy(tf)
    st.header(header)
    df=sit.long_term_df
    df2=sit.short_term_df
    ################################################################## Current Trend ######################################################################################
    if op['Bullish Trend'] : 
        st.subheader('Bullish Trend')
        st.write('1 Point')
    if thr['Bearish Trend'] : 
        st.subheader('Bearish Trend')
        st.write('-1 Point')


    fig=DrawCandleSticks(df,df2)
    trend_points=[sit.short_trend_points,sit.long_trend_points]

    for i in range(0,2):
        trend_down_xs=[trend_points[i][0][0][0],trend_points[i][0][1][0]]
        trend_down_ys=[trend_points[i][0][0][1],trend_points[i][0][1][1]]

        trend_up_xs=[trend_points[i][1][0][0],trend_points[i][1][1][0]]
        trend_up_ys=[trend_points[i][1][0][1],trend_points[i][1][1][1]]

        trend_down_xs_time=pd.to_datetime(trend_down_xs,unit='ms')
        fig.add_trace(
            go.Scatter(x=trend_down_xs_time, y=trend_down_ys, line=dict(
                color="gray",width=0.5), name=f'support'), row=1, col=1
        )                           

        trend_up_xs_time=pd.to_datetime(trend_up_xs,unit='ms')
        fig.add_trace(
            go.Scatter(x=trend_up_xs_time, y=trend_up_ys, line=dict(
                color="gray",width=0.5), name=f'resist'), row=1, col=1
        )         
    if sit.trend_break_level>0:
        pa_beark_level_xs=[df.iloc[0].timestamp,df.iloc[-1].timestamp]
        pa_break_level_ys=[sit.trend_break_level,sit.trend_break_level]
        pa_beark_level_xs_time=pd.to_datetime(pa_beark_level_xs,unit='ms')
        fig.add_trace(
            go.Scatter(x=pa_beark_level_xs_time, y=pa_break_level_ys, line=dict(
                color="#e05293",width=0.75), name=f'Trend Break Level'), row=1, col=1
        )         

    fig.update_layout(xaxis_rangeslider_visible=False,
                        height=450)
    st.plotly_chart(fig, use_container_width=True)

    ################################################################## Static Levels ######################################################################################
    hraders_levels=['Current Static Levels','Parent Static Levels']
    ops_levels=['Candle Above Static Level','Candle Above Parent Static Level']
    static_levels=[sit.static_levels]
    if sit.parent_static_levels !=[]:
        static_levels.append(sit.parent_static_levels)
    max_level=df2['high'].values.max()
    min_level=df2['low'].values.min()

    for i in range(0,len(static_levels)):
        st.subheader(hraders_levels[i])
        if op[ops_levels[i]]:
            st.write('0.5 Point')
        else:
            st.write('0 Point')
        fig=DrawCandleSticks(df,df2,both=False)
        for l in static_levels[i]:
            if l[1]<=max_level and l[0]>=min_level:
                for i in range(0,2):
                    level_xs=[df2.iloc[0].timestamp,df2.iloc[-1].timestamp]
                    level_ys=[l[i],l[i]]
                    level_xs_time=pd.to_datetime(level_xs,unit='ms')
                    fig.add_trace(
                    go.Scatter(x=level_xs_time, y=level_ys, line=dict(
                        color="#e05293",width=0.55), name=f'Parent Level'), row=1, col=1
        )         

        fig.update_layout(xaxis_rangeslider_visible=False,
                            height=450)
        st.plotly_chart(fig, use_container_width=True)

    ################################################################## Dynamic Support/Resistant ######################################################################################

    st.subheader('Candle Above Dynamic Support')
    if op['Near Support']:
        st.write('1.5 point')
    else:
        st.write('0 point')

    fig=DrawCandleSticks(df,df2,both=False)
    sup_xs=[df2.iloc[0].timestamp,df2.iloc[-1].timestamp]
    sup_ys_start=sit.dynamic_support_line['p0_y']-(sit.dynamic_support_line['p0_x']-sup_xs[0])*sit.dynamic_support_line['m']
    sup_ys_end=sit.dynamic_support_line['p0_y']+(sup_xs[1]-sit.dynamic_support_line['p0_x'])*sit.dynamic_support_line['m']
    sup_ys=[sup_ys_start,sup_ys_end]
    sup_xs_time=pd.to_datetime(sup_xs,unit='ms')
    fig.add_trace(
    go.Scatter(x=sup_xs_time, y=sup_ys, line=dict(
        color="#e05293",width=0.55), name=f'Dynamic Support, R2={sit.dynamic_support_line["r2"]}'), row=1, col=1
    )

    fig.update_layout(xaxis_rangeslider_visible=False,
                        height=450)
    st.plotly_chart(fig, use_container_width=True)

    ################################################################## Current Ichi Moko ######################################################################################
    st.subheader('Ichi Moko Status')

    if (op['Above Ichi']==True):
        st.write('0.3 point')
    else:
        st.write('0 point')


    # if st.button("Draw Points"):
        
        






first=True
with st.container():
    cols = st.columns([1, 1, 1, 1])
    tfs = ['1d', '4h', '1h', '15m']
    if exch == 'Yahoo':
        tfs = ['1d', '90m', '60m', '15m']

    for i in range(0, len(tfs)):
        if cols[i].button(tfs[i]):
            tf = tfs[i]
            st.experimental_set_query_params(tf=tf, exch=exch, symbol=symbol)            
            first=False
            DoAnalysis()
            
if first: DoAnalysis()
