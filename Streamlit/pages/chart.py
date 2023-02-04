import streamlit as st
import pandas as pd
import helper
import pivot_helper
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talibHelper import AllPatterns as alp
from sklearn import preprocessing, model_selection, svm
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from matplotlib import style
import datetime
import plotly.figure_factory as ff
import MarketReader as mr

local = False
st. set_page_config(layout="wide")
st.markdown("""

        <style>
                ..css-k1ih3n {
                    padding: 0;
                }

        </style>
        """, unsafe_allow_html=True)

symbol = None
tf = None
exch = None
q = st.experimental_get_query_params()
if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
if (q.__contains__('tf')):
    tf = q['tf'][0]
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


def is_consolidating(closes, percentage=2):
    max_close = closes.max()
    min_close = closes.min()
    threshold = 1-(percentage/100)
    if min_close > (max_close * threshold):
        return True
    return False


def brout_check(df, candles=15):
    for index in df.index:
        if (index >= candles):
            last_close = df['close'][index]
            if (is_consolidating(df['close'][index-candles-1:index-1], percentage=10)):
                if (last_close > df['close'][index-candles-1:index-1].max()):
                    df['brout'][index] = 1
                else:
                    df['brout'][index] = np.nan
            else:
                df['brout'][index] = np.nan
        else:
            df['brout'][index] = np.nan

    return df

def fillcol(label):
    if label >= 1:
        return 'rgba(236,245,236,0.4)'
    else:
        return 'rgba(232,178,178,0.4)'

def DrawChart(limit=500, read_patterns=False, read_rsi=False, read_bb=True, read_sma=False, read_ichi=True, read_ema=False, read_vol=True, read_fi=False, chart_height=800,
              entry_signals=True, exit_signals=False, entry_signal_mode='All', left_candles=3, right_candles=3, waves_number=3):
    if (symbol != None and tf != None and exch != None):

        read_bull_patterns = read_patterns
        read_bear_patterns = read_patterns
        patterns_res = False
        read_rsi = read_rsi
        read_bb = read_bb
        read_sma = read_sma
        read_ema = read_ema
        read_vol = read_vol

        df = helper.GetData(tf, symbol, exch)
        if (df.size):
            limit = limit
            if (len(df) < limit):
                limit = len(df)
            df = pd.DataFrame(data=df[-limit:]).reset_index(drop=True)
            df, up_points, down_points, sidepoints, power_ups, power_downs, power_weaking_ups, power_weaking_downs = pivot_helper.find_pivots(
                df, left_candles, right_candles, waves_number)

            if (read_bull_patterns):
                try:
                    patterns_res, ndf = alp(df)
                except:
                    patterns_res = False

            cond = [read_bull_patterns, read_bear_patterns,
                    read_rsi, read_vol, read_fi]
            rownum = 1 + len([x for x in cond if x == True])
            row_heights = [0.7]
            for k in range(0, rownum-1):
                row_heights.append(0.4/(rownum-1))
            fig = make_subplots(
                rows=rownum, cols=1,
                column_widths=[1],
                row_heights=row_heights,
                shared_xaxes=True, vertical_spacing=0.01,
            )
            # df['upperband'],df['middleband'],df['lowerband']=tah.BoolingerBands(close= df['close'],timeperiod= 20, nbdevdn= 6, nbdevup= 6, matype=0)

            pointpos_df = pd.DataFrame(
                data=df[~pd.isnull(df['pointpos'])], columns=['time', 'pointpos'])
            # st.dataframe(df)
            fig.add_trace(
                go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=pointpos_df['time'], y=pointpos_df['pointpos'], line=dict(
                    color="#3d5ab2"), name='wave line')
            )
            fig.add_trace(
                go.Scatter(x=df['time'], y=power_ups, mode='markers', marker=dict(
                    size=10, color="green", symbol='star'), name='strong up')
            )
            fig.add_trace(
                go.Scatter(x=df['time'], y=power_downs, mode='markers', marker=dict(
                    size=10, color="red", symbol='star'), name='strong down')
            )
            fig.add_trace(
                go.Scatter(x=df['time'], y=power_weaking_ups, mode='markers', marker=dict(
                    size=10, color="green", symbol='circle-open'), name='weak up')
            )
            fig.add_trace(
                go.Scatter(x=df['time'], y=power_weaking_downs, mode='markers', marker=dict(
                    size=10, color="red", symbol='circle-open'), name='weak down')
            )
            rownum = 1
            if (read_ichi):
                helper.append_ichi(df)
                df_copy=df.copy()

                df_copy['label']=np.where(df['ich_komo_color']>0,1,0)
                df_copy['group'] = df_copy['label'].ne(df_copy['label'].shift()).cumsum()
                df_copy=df_copy.groupby('group')
                dfs=[]
                for name , data in df_copy:
                    dfs.append(data)
                for d in dfs:
                    # dot_opacity=np.ones(len(d))
                    # dot_opacity[0]=0

                    fig.add_trace(
                        go.Scatter(x=d['time'], y=d['ich_a'] , name='trace',line=dict(color="white",width=0),mode='lines'), row=rownum, col=1,
                    )
                    fig.add_trace(
                        go.Scatter(x=d['time'], y=d['ich_b'] ,fill='tonexty',fillcolor=fillcol(d['label'].iloc[0]) , name ='trace',line=dict(color="white",width=0),mode='lines'), row=rownum, col=1
                    )
                for trace in fig['data']:
                    if(trace['name'] == 'trace'):
                        trace['showlegend'] = False

                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_a'], name='span a', line=dict(color="green",width=0.7)), row=rownum, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_b'], name='span b', line=dict(color="red",width=0.7)), row=rownum, col=1
                )

                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_base_line'], name='ichi_base_line', line=dict(color="blue",width=1)), row=rownum, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_conversion_line'], name='ichi_conversion_line', line=dict(color="red",width=1)), row=rownum, col=1
                )
                           
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
          
            helper.append_adx(df)
            if (entry_signals):
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['adx_signal_marker'], mode='markers', marker=dict(
                        size=8, symbol="star-triangle-up", line=dict(width=2, color=3)), name='adx entry signal')

                )

            if (read_fi):
                rownum += 1
                helper.append_fi(df)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['fi_norm'], name='fi_norm'), row=rownum, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['fi_entry_signal'], mode='markers', marker=dict(
                            size=8, symbol="arrow-wide", line=dict(width=2, color=2)), name='fi entry signal')
                    )

            if (read_bb):
                helper.append_bb(df, entry_signal=entry_signals,
                                 entry_signal_mode=entry_signal_mode)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['middleband'], name='middle band'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['upperband'], name='upper band'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['lowerband'], name='lower band'), row=1, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['bb_entry_signal'], mode='markers', marker=dict(size=8, symbol="circle", line=dict(width=2, color=1.5)), name='bb entry signal'), row=1, col=1
                    )
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['bb_sq_entry_signal'], mode='markers', marker=dict(size=8, symbol="circle-x", line=dict(width=2, color=1.5)), name='bb squeez entry signal'), row=1, col=1
                    )
            if (False):
                df['brout'] = np.nan
                df = brout_check(df.reset_index(), candles=15)
                df1 = pd.DataFrame(data=df, columns=['time', 'close'])
                df2 = pd.DataFrame(data=df, columns=['time', 'brout']).dropna()
                df3 = pd.DataFrame(df2).merge(pd.DataFrame(df1), on='time')
                fig.add_trace(
                    go.Scatter(x=df3['time'], y=df3['close'], mode='markers', marker=dict(size=3, symbol="triangle-up", line=dict(width=2, color=2.5)), name='break out'), row=1, col=1
                )
            if (read_rsi):
                rownum += 1
                helper.append_rsi(df, entry_signal=entry_signals,
                                  entry_signal_mode=entry_signal_mode)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['rsi'], name='rsi'), row=rownum, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['rsi_entry_signal'], mode='markers', marker=dict(size=8, symbol="diamond", line=dict(width=2, color=1.5)), name='rsi entry signal'), row=1, col=1
                    )
            if (read_vol):
                rownum += 1
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['volume'], name='Volume'), row=rownum, col=1
                )
            if (read_sma):
                helper.append_sma(df, entry_signal=entry_signals,
                                  entry_signal_mode=entry_signal_mode)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_5'], name='sma 5'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_10'], name='sma 10'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_30'], name='sma 30'), row=1, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['sma_entry_signal'], mode='markers', marker=dict(
                            size=8, symbol="asterisk", line=dict(width=2, color="DarkSlateGrey")), name='sma entry signal')
                    )

            if (read_ema):
                helper.append_ema(df, entry_signal=entry_signals,
                                  entry_signal_mode=entry_signal_mode)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_5'], name='ema 5'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_10'], name='ema 10'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ema_30'], name='ema 30'), row=1, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['ema_entry_signal'], mode='markers', marker=dict(
                            size=8, symbol="x-thin", line=dict(width=2, color="DarkSlateGrey")), name='ema entry signal')
                    )
       
            helper.append_macd(df)

            fig.update_layout(xaxis_rangeslider_visible=False,
                              height=chart_height)
            st.plotly_chart(fig, use_container_width=True)

            # # fig2.update_xaxes(type='category')
            # st.plotly_chart(fig2,use_container_width=True)
            # st.set_option('deprecation.showPyplotGlobalUse', False)

    else:
        st.write('no param')


def PredictPrice(coin, tf, forecast_out=20):
    style.use('ggplot')
    df0 = helper.GetData(tf=tf, symbol=coin, exch='Kucoin')
    helper.append_rsi(df=df0, entry_signal=True, entry_signal_mode='All')
    helper.append_fi(df=df0)
    helper.append_adx(df=df0)
    helper.append_bb(df=df0, entry_signal=True, entry_signal_mode='All')
    helper.append_sma(df=df0, entry_signal=True, entry_signal_mode='All')
    helper.append_ema(df=df0, entry_signal=True, entry_signal_mode='All')
    unixdict = {'30m': 1800, '1h': 3600, '4h': 14400, '1d': 86400}
    # df0=df0[-1200:]

    df = df0[:-forecast_out]
    # df=df[['time','close','open','high','low','volume']]
    df['hl_pct'] = (df['high']-df['low'])/df['low'] * 100
    df['pct_change'] = (df['close']-df['open'])/df['low'] * 100
    df = df[['time', 'close', 'volume', 'hl_pct', 'pct_change',
             'rsi_entry_signal', 'pband', 'fi_norm', 'adx_pos_neg']]
    forecast_col = 'close'
    df.fillna(-99999, inplace=True)

    # forecast_out=int(math.ceil(0.015*len(df)))
    print(forecast_out)

    df['label'] = df[forecast_col].shift(-forecast_out)

    X = np.array(df.drop(['time', 'label'], 1))
    X = preprocessing.scale(X)
    X = X[:-forecast_out]
    X_lately = X[-forecast_out:]

    df.dropna(inplace=True)

    y = np.array(df['label'])
    print(10*'*')
    X_train, X_test, y_train, y_test = model_selection.train_test_split(
        X, y, test_size=0.2)
    clf = LinearRegression()
    clf.fit(X_train, y_train)
    accuracy = clf.score(X_test, y_test)

    forecast_set = clf.predict(X_lately)
    real_set = np.array(df0['close'][-forecast_out:])

    print(forecast_set)
    print(real_set)
    print((real_set-forecast_set)/real_set*100)

    print(accuracy)
    df['forecast'] = np.nan
    last_time = df.iloc[-1].time
    last_unix = last_time.timestamp()
    one_tf = unixdict[tf]
    next_unix = last_unix+one_tf

    for price in forecast_set:
        next_timestamp = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_tf
        df.loc[next_timestamp] = [
            np.nan for _ in range(len(df.columns)-1)] + [price]

    ff.create_distplot(df['close'], group_labels='X')
    df['close'].plot()
    df0['close'].plot()
    df['forecast'].plot()
    plt.xlabel = 'Date'
    plt.ylabel = 'Price'
    plt.show()

    st.plotly_chart(ff)


def DrawTheChart():
    DrawChart(limit=limit, read_vol=vol_check, read_bb=bb_check,
              read_ema=ema_check, read_sma=sma_check, read_ichi=ichi_check, read_patterns=patterns_check, read_rsi=rsi_check,
              entry_signals=entry_signals_check, entry_signal_mode=entry_signal_mode, left_candles=pivot_candle_left, right_candles=pivot_candle_right, waves_number=waves_number)


st.sidebar.title("Chart parameters: ")


with st.sidebar:
    limit = st.number_input("Data Limit:", min_value=100, value=200)
    st.write("Pivot Settings:")
    pivot_candle_left = st.number_input("Left Camndles:", min_value=2, value=7)
    pivot_candle_right = st.number_input(
        "Right Camndles:", min_value=2, value=7)
    st.write('Price Action Settings:')
    waves_number = st.number_input("Number of Waves:", min_value=2, value=3)

    st.write("Indicators")
    ichi_check = st.checkbox("Ichi Komo", value=True)
    sma_check = st.checkbox("SMA", value=False)
    rsi_check = st.checkbox("RSI", value=True)
    bb_check = st.checkbox("Bollinger bands", value=False)
    patterns_check = st.checkbox("Patterns", value=False)
    ema_check = st.checkbox("EMA", value=False)
    vol_check = st.checkbox("Volume", value=False)
    entry_signals_check = st.checkbox("Entry Signals", value=True)
    if (entry_signals_check):
        entry_signal_names = ['All', 'Uptrend']
        entry_signal_mode = st.radio("Entry Signal Mode", entry_signal_names)
    else:
        entry_signal_mode = 'None'
    ML_check = st.checkbox("ML Predict", value=False)
    if (ML_check):
        forecast_out = st.number_input(
            "Forecast Number:", min_value=5, max_value=30, value=20)
        if st.button('ML Predict Price'):
            if (q.__contains__('symbol') and q.__contains__('tf')):
                symbol = q['symbol'][0]
                tf = q['tf'][0]
                PredictPrice(coin=symbol, tf=tf, forecast_out=forecast_out)

with st.container():
    cols = st.columns([1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1])
    if cols[0].button('5m'):
        tf = '5m'
        st.experimental_set_query_params(tf='5m', exch=exch, symbol=symbol)
    if cols[1].button('15m'):
        tf = '15m'
        st.experimental_set_query_params(tf='15m', exch=exch, symbol=symbol)
    if cols[2].button('30m'):
        tf = '30m'
        st.experimental_set_query_params(tf='30m', exch=exch, symbol=symbol)
    if cols[3].button('1h'):
        tf = '1h'
        st.experimental_set_query_params(tf='1h', exch=exch, symbol=symbol)
    if cols[4].button('4h'):
        tf = '4h'
        st.experimental_set_query_params(tf='4h', exch=exch, symbol=symbol)
    if cols[5].button('1d'):
        tf = '1d'
        st.experimental_set_query_params(tf='1d', exch=exch, symbol=symbol)
    if cols[6].button('Download Latest'):
        if (symbol.lower().__contains__('usdt')):
            mr.ReadKucoinMarket(timeframes=['5m', '15m', '30m', '1h', '4h', '1d'],
                                local=local, testdata=False, symbol=symbol.replace('_', '/').upper())

DrawTheChart()
