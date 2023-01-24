import streamlit as st
import pandas as pd
import helper , pivot_helper
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talibHelper import AllPatterns as alp
from sklearn import preprocessing , model_selection , svm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
import plotly.figure_factory as ff

Base_DIR = '/root/trader_webapp/'
relp = True
st. set_page_config(layout="wide")
st.markdown("""

        <style>
                .css-1vq4p4l {
                    padding: 2rem 1rem 1.5rem;
                }
               .css-18e3th9 {
                    padding-top: 2rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)



def ScanMarkets():
    uptrends=[]
    downtrends=[]
    link_style_text='background-color:transparent;border:none;text-decoration: underline; color:#21a58a; font-size:large'
    markets=helper.GetAllData()
    for m in markets:
        df , _ , _ , _ = pivot_helper.find_pivots(list(m.values())[0],3,3)
        df= df[~pd.isnull(df['pivot_trend'])]
        if df[-1:]['pivot_trend'].values[0]=='up' and df[-1:]['pivot'].values[0]==2:
            key=list(m.keys())[0]
            sym=key.split('__')[0]
            tf=key.split('__')[1].split('.')[0]

            chart_url='http://trader.baharsoft.com:8100/chart?symbol={}&exch=Kucoin&tf={}'.format(sym.upper(),tf)
            
            link = f'[{sym.replace("_","/")}]({chart_url})'
            
            st.markdown(link,unsafe_allow_html=True)

st.sidebar.title("Options: ")
with st.sidebar:
    operation=st.selectbox("Choose Market:",options=['Crypto (Kucoin)'])


# ScanMarkets()
#if st.button('Scan Market'):
    #ScanMarkets()
