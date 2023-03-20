from statistics import mean
import streamlit as st
import pandas as pd
import helper , Constants as c
import pivot_helper
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talibHelper import AllPatterns as alp
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
import plotly.figure_factory as ff
import MarketReader as mr
import situations as s

local = False


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

symbol = 'BTC_USDT'
exch = 'Kucoin'
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
            "Short Term Trend Limit:", min_value=20, value=70)
        st.write("1d Pivot Settings:")
        long_term_pivot_candles = st.number_input(
            "Long Term Candles:", min_value=2, value=16)
        short_term_pivot_candles = st.number_input(
            "Short Term Candles:", min_value=2, value=6)
        waves_number = st.number_input(
            "PA Power Calc. Waves:", min_value=2, value=2)
        sr_limit = st.number_input("S/R Limit:", min_value=70, value=120)


if analysis == '1.0':
    dict = {}
    tfs = ['1d', '4h', '1h', '15m']
    # Daily Analysis
    for tf in tfs:

        df = helper.GetData(tf, symbol, exch)
        df_long = df[-trend_limit_long:].reset_index(drop=True)
        df_short = df[-trend_limit_short:].reset_index(drop=True)
        df_long, up_points, down_points, sidepoints, power_ups, power_downs, power_weaking_ups, power_weaking_downs = pivot_helper.find_pivots(
            df_long, long_term_pivot_candles, long_term_pivot_candles, waves_number, short=False)
        df_short, _, _, _, _, _, _, _ = pivot_helper.find_pivots(
            df_short, 2, 2, 2, short=False)

        trend_long = helper.TrendDirection(df_long)
        trend_short = helper.TrendDirection(df_short)
        pa_break, is_break = helper.PA_Break(
            df_long, trend_long, trend_short)

        important_levels = helper.GetImportantLevels(
            df_long, threshold=0.01, combined=True)

        helper.append_ichi(df)
        ichi_status = helper.GetIchiStatus(df)
        db_bot, db_top = helper.double_levels(df, threshold=0.01)

        current_trend=c.Trend.Nothing
        if trend_long == c.Trend.Bullish:
            if (trend_short == c.Trend.Bearish and not is_break) or (trend_short == c.Trend.Bullish):
                current_trend=c.Trend.Bullish
            else:
                current_trend=c.Trend.Bearish
        elif trend_long == c.Trend.Bearish:
            if (trend_short == c.Trend.Bullish and not is_break) or (trend_short == c.Trend.Bearish):
                current_trend=c.Trend.Bearish
            else:
                current_trend=c.Trend.Bullish

        
        S_stat,candle_S_stat,R_stat,candle_R_stat=helper.Dynamic_SR(df_short,threshold=0.015,n=3)
        p0_sup_x,p0_sup_y,m_sup,r2_sup=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=3,mode=1)
        p0_res_x,p0_res_y,m_res,r2_res=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=3,mode=2)

        fibo_dir_retrace,fibo_stat_retrace,fibo_retrace_levels=helper.FiboStat(df=df_short,fibomode=c.Fibo_Mode.Retracement,threshold=0.015)
        fibo_dir_trend,fibo_stat_trend,fibo_trend_levels=helper.FiboStat(df=df_long,fibomode=c.Fibo_Mode.Trend_Base_Extension,threshold=0.015)
        fibo_data_retrace={'dir':fibo_dir_retrace,'stat':fibo_stat_retrace,'levels':fibo_retrace_levels}
        fibo_data_trend={'dir':fibo_data_trend, 'stat':fibo_stat_trend,'levels':fibo_trend_levels}
        last_candle_color=c.Candle_Color.Red
        if df_short[-1:]['close'].values[0]>df_short[-1:]['open'].values[0]:
            last_candle_color=c.Candle_Color.Green


        dict[tf] = {'last_candle_color':last_candle_color, 
                    'df_long':df_long,'df_short':df_short,'long_trend': trend_long, 'short_trend': trend_short, 'current_trend':current_trend,
                    'pa_break': pa_break, 'is_break': is_break, 
                    'important_levels': important_levels,
                    'support_dynamic_trend':{'p0_x':p0_sup_x,'p0_y':p0_sup_y,'m':m_sup,'r2':r2_sup},
                    'resist_dynamic_trend':{'p0_x':p0_res_x,'p0_y':p0_res_y,'m':m_res,'r2':r2_res},
                    'ichi_stat': ichi_status, 'double_bot_level': db_bot,'double_top_level': db_top,
                    'fibo':{'retrace':fibo_data_retrace,'trend':fibo_data_trend},
                    'dynamic_support':{'trend_stat':S_stat,'candle_stat':candle_S_stat},
                    'dynamic_resist':{'trend_stat':R_stat,'candle_stat':candle_R_stat}}
    
    situations={}
    for tf in dict:
        candle=dict[tf]['df_short'][-1:]
        sit=s.Situation()
        sit.tf=tf
        sit.candle_color=dict[tf]['last_candle_color']
        sit.ichi_stat=dict[tf]['ichi_stat']
        sit.long_trend_stat=dict[tf]['trend_long']
        sit.short_trend_stat=dict[tf]['short_trend']
        sit.current_trend_stat=dict[tf]['current_trend']
        sit.dynamic_support_stat=dict[tf]['support_closeness'][1]
        sit.dynamic_resist_stat=dict[tf]['resist_closeness'][1]
        sit.fibo_level_retrace_stat=dict[tf]['fibo']['retrace']['stat']
        sit.fibo_level_trend_stat=dict[tf]['fibo']['trend']['stat']

        tf_parent_index=tfs.index (tf)-1
        
        if tf_parent_index>=0:
            tf_p=tfs[tf_parent_index]
            levels_parent=dict[tf_p]['important_levels']
            for l in levels_parent:
                candle_stat=helper.Candle_level_stat(l[1],l[0],candle)
                if candle_stat!=c.Candle_Level_Area_Stat.Nothing:
                    sit.parent_level_stat=candle_stat
                    break
            sit.parent_dynamic_support_stat,sit.parent_dynamic_resist_stat=helper.Candle_Dynamic_Trend_Stat(candle=candle,supp_data=dict[tf_p]['support_dynamic_trend'],res_data=dict[tf_p]['resist_dynamic_trend'],r_min=0.95,threshold=0.01)

            sit.fibo_parent_level_retrace_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['retrace']['levels'],tf=tf_p,thb=1)
            sit.fibo_parent_level_retrace_dir=dict[tf_p]['fibo']['retrace']['dir']
            sit.fibo_parent_level_trend_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['trend']['levels'],tf=tf_p, thb=1)
            sit.fibo_parent_level_trend_dir=dict[tf_p]['fibo']['trend']['dir']
            
        sit.candle_shapes=helper.Candle_Shapes(candle=candle,tf=tf,thb=1)
        sit.double_bot_happened=dict[tf]['double_bot_level'] 
        sit.double_top_happened=dict[tf]['double_top_level'] 

        situations[tf]=sit




                    




        

    

    st.write(dict)
