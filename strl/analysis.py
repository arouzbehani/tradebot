import situations as s
import streamlit as st
import helper , Constants as c
import analaysis_constants as ac
import analyzer as a 
from plotly.subplots import make_subplots
import plotly.graph_objects as go
# from statistics import mean
# import plotly.graph_objects as go
import numpy as np
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

tf='4h'
symbol = 'TRX_USDT'
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
        candles_back=st.number_input("Candles Back:",min_value=0,value=0)
        trend_limit_long = st.number_input(
            "Long Term Trend Limit:", min_value=70, value=ac.Long_Term_Trend_Limit)
        trend_limit_short = st.number_input(
            "Short Term Trend Limit:", min_value=20, value=ac.Short_Term_Trend_Limit)
        st.write("1d Pivot Settings:")
        long_term_pivot_candles = st.number_input(
            "Long Term Candles:", min_value=2, value=ac.Long_Term_Candles)
        short_term_pivot_candles = st.number_input(
            "Short Term Candles:", min_value=2, value=ac.Short_Term_Candles)
        pvt_trend_number = st.number_input(
            "Pivot Trend Number:", min_value=2, value=ac.Pivot_Trend_Number)
        
        waves_number = st.number_input(
            "PA Power Calc. Waves:", min_value=2, value=ac.PA_Power_Calc_Waves)
        threshold=st.number_input("Closeness Threshold (%):",min_value=0.1,value=ac.Threshold,max_value=5.0,step=0.1)
        sr_limit = st.number_input("S/R Limit:", min_value=70, value=ac.S_R_Limit)

            
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


def fillcol(label):
    if label >= 1:
        return 'rgba(236,245,236,0.4)'
    else:
        return 'rgba(232,178,178,0.4)'

def DoAnalysis():
    #tf='1h'
    analyzer=a.Analyzer()
    analyzer.init_data(tfs=tfs,exch=exch,symbol=symbol,trend_limit_long=trend_limit_long,trend_limit_short=trend_limit_short,long_term_pivot_candles=long_term_pivot_candles,short_term_pivot_candles=short_term_pivot_candles,
                    pvt_trend_number=pvt_trend_number,waves_number=waves_number,candles_back=candles_back,th=threshold/100)
    sit=s.Situation()
    sit=analyzer.situations[tf]
    dict_buy_sell=analyzer.buy_sell(tf)
    buy_pars=s.Parametrs()
    sell_pars=s.Parametrs()
    buy_pars=dict_buy_sell['buy']
    sell_pars=dict_buy_sell['sell']
    total_point=buy_pars.calc_points()-sell_pars.calc_points()
    st.header(f'{tf} Total Point: {total_point}')
    st.markdown("""---""")
   
    df=sit.long_term_df
    df2=sit.short_term_df
    ################################################################## Price Action Trend ######################################################################################
    st.subheader('Price Action Trend')
    st.write(f'Buy Point: {buy_pars.price_action_trend[0]*buy_pars.price_action_trend[1]}')
    st.write(f'Sell Point: {sell_pars.price_action_trend[0] * sell_pars.price_action_trend[1]}')
    

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
    st.markdown("""---""")

    ################################################################## Static Levels ######################################################################################

    hraders_levels=['Current Static Levels','Parent Static Levels']
    static_levels=[sit.static_levels]
    static_buy_points=[buy_pars.static_SR_closeness[0]*buy_pars.static_SR_closeness[1],buy_pars.static_SR_closeness_parent[0]*buy_pars.static_SR_closeness_parent[1]]
    static_sell_points=[sell_pars.static_SR_closeness[0]*sell_pars.static_SR_closeness[1],sell_pars.static_SR_closeness_parent[0]*sell_pars.static_SR_closeness_parent[1]]
    if sit.parent_static_levels !=[]:
        static_levels.append(sit.parent_static_levels)
    max_level=df2['high'].values.max()*1.1
    min_level=df2['low'].values.min()*0.9
    static_level_colors=["#93e2ec","#e05293"]

    for i in range(0,len(static_levels)):
        st.subheader(hraders_levels[i])
        st.write(f'Buy Point: {static_buy_points[i]}')
        st.write(f'Sell Point: {static_sell_points[i]}')

        fig=DrawCandleSticks(df,df2,both=False)
        for l in static_levels[i]:
            if l[1]<=max_level and l[0]>=min_level:
                for i in range(0,2):
                    level_xs=[df2.iloc[0].timestamp,df2.iloc[-1].timestamp]
                    level_ys=[l[i],l[i]]
                    level_xs_time=pd.to_datetime(level_xs,unit='ms')
                    fig.add_trace(
                    go.Scatter(x=level_xs_time, y=level_ys, line=dict(
                        color=f"{static_level_colors[i]}",width=0.55), name=f'Static Level {i+1}'), row=1, col=1
        )         

        fig.update_layout(xaxis_rangeslider_visible=False,
                            height=450)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("""---""")

    ################################################################## Dynamic Support/Resistant ######################################################################################

    hraders_SR=['Dynamic SR','Parent Dynamic SR']
    dynamic_sr_buy_points=[buy_pars.dynamic_SR_closeness[0]*buy_pars.dynamic_SR_closeness[1],buy_pars.dynamic_SR_closeness_parrent[0]*buy_pars.dynamic_SR_closeness_parrent[1]]
    dynamic_sr_sell_points=[sell_pars.dynamic_SR_closeness[0]*sell_pars.dynamic_SR_closeness[1],sell_pars.dynamic_SR_closeness_parrent[0]*sell_pars.dynamic_SR_closeness_parrent[1]]

    lines=[[sit.dynamic_support_line,sit.dynamic_resist_line]]
    if sit.dynamic_support_line_parent!={} and sit.dynamic_resist_line_parent!={}:
          lines.append([sit.dynamic_support_line_parent,sit.dynamic_resist_line_parent])
    legends=['Dynamic Support','Dynamic Resist']
    colors=['#52b47f','#e05293']
    xs=[df2.iloc[0].timestamp,df2.iloc[-1].timestamp]
    for i in range(0,len(lines)):
        st.subheader(hraders_SR[i])
        st.write(f'Buy Point: {dynamic_sr_buy_points[i]}')
        st.write(f'Sell Point: {dynamic_sr_sell_points[i]}')

        fig=DrawCandleSticks(df,df2,both=False)
        for j in range(0,2):
            ys_start=lines[i][j]['p0_y']-(lines[i][j]['p0_x']-xs[0])*lines[i][j]['m']
            ys_end=lines[i][j]['p0_y']+(xs[1]-lines[i][j]['p0_x'])*lines[i][j]['m']
            ys=[ys_start,ys_end]
            xs_time=pd.to_datetime(xs,unit='ms')
            fig.add_trace(
            go.Scatter(x=xs_time, y=ys, line=dict(
                color=f"{colors[j]}",width=0.55), name=f'{legends[j]}, R2={lines[i][j]["r2"]}'), row=1, col=1
            )

        fig.update_layout(xaxis_rangeslider_visible=False,
                            height=450)
        st.plotly_chart(fig, use_container_width=True)

    ################################################################## Current Ichi Moko ######################################################################################
    hraders_ichi=['Ichi Moku Status','Parent Ichi Moku Status']
    ichi_buy_points=[buy_pars.ichi_location[0]*buy_pars.ichi_location[1],buy_pars.ichi_location_parent[0]*buy_pars.ichi_location_parent[1]]
    ichi_sell_points=[sell_pars.ichi_location[0]*sell_pars.ichi_location[1],sell_pars.ichi_location_parent[0]*sell_pars.ichi_location_parent[1]]
    dfs=[[df2,df2.copy()]]
    if len(sit.short_term_df_parent)>0:
        dfs.append([sit.short_term_df_parent, sit.short_term_df_parent.copy()])
    for i in range(len(dfs)):
        st.subheader(hraders_ichi[i])
        st.write(f'Buy Point: {ichi_buy_points[i]}')
        st.write(f'Sell Point: {ichi_sell_points[i]}')
        fig=DrawCandleSticks(dfs[i][0],dfs[i][0],both=False)
        df_copy = dfs[i][1]
        helper.append_ichi(dfs[i][0])

        df_copy['label'] = np.where(dfs[i][0]['ich_moku_color'] > 0, 1, 0)
        df_copy['group'] = df_copy['label'].ne(
            df_copy['label'].shift()).cumsum()
        df_copy = df_copy.groupby('group')
        all_dfs = []
        for name, data in df_copy:
            all_dfs.append(data)
        for d in all_dfs:
            fig.add_trace(
                go.Scatter(x=d['time'], y=d['ich_a'], name='trace', line=dict(color="white", width=0), mode='lines'), row=1, col=1,
            )
            fig.add_trace(
                go.Scatter(x=d['time'], y=d['ich_b'], fill='tonexty', fillcolor=fillcol(d['label'].iloc[0]), name='trace', line=dict(color="white", width=0), mode='lines'), row=1, col=1
            )
        for trace in fig['data']:
            if (trace['name'] == 'trace'):
                trace['showlegend'] = False

        fig.add_trace(
            go.Scatter(x=dfs[i][0]['time'], y=dfs[i][0]['ich_a'], name='span a', line=dict(color="green", width=0.7)), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=dfs[i][0]['time'], y=dfs[i][0]['ich_b'], name='span b', line=dict(color="red", width=0.7)), row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=dfs[i][0]['time'], y=dfs[i][0]['ich_base_line'], name='ichi_base_line', line=dict(color="blue", width=1)), row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=dfs[i][0]['time'], y=dfs[i][0]['ich_conversion_line'], name='ichi_conversion_line', line=dict(color="red", width=1)), row=1, col=1
        )
        fig.update_layout(xaxis_rangeslider_visible=False,
                            height=450)
        st.plotly_chart(fig, use_container_width=True)

        
        






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

