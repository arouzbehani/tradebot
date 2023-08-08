import itertools
from statistics import mean
import streamlit as st
import pandas as pd
import helper,GLOBAL
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

local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True

def getTilte():
    q = st.experimental_get_query_params()
    if (q.__contains__('symbol')):
        return q['symbol'][0]
    return "Chart"


st. set_page_config(layout="wide", page_title=getTilte())
st.markdown("""

        <style>
                ..css-k1ih3n {
                    padding: 0;
                }

        </style>
        """, unsafe_allow_html=True)
# symbol = 'FTM_USDT'
# tf = '1h'
# exch = 'kucoin'
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


def best_fit_slope_and_intercept(xs, ys):
    m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
         ((mean(xs)*mean(xs)) - mean(xs*xs)))
    b = mean(ys) - m*mean(xs)
    return m, b


def squared_error(ys_orig, ys_line):
    return sum((ys_line - ys_orig) * (ys_line - ys_orig))


def coefficient_of_determination(ys_orig, ys_line):
    y_mean_line = [mean(ys_orig) for y in ys_orig]
    squared_error_regr = squared_error(ys_orig, ys_line)
    squared_error_y_mean = squared_error(ys_orig, y_mean_line)
    return 1 - (squared_error_regr/squared_error_y_mean)


def r2(xs, ys):
    m, b = best_fit_slope_and_intercept(xs, ys)
    regression_line = [(m*x)+b for x in xs]
    r_squared = coefficient_of_determination(ys, regression_line)
    return r_squared


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
              entry_signals=True, exit_signals=False, entry_signal_mode='All', left_candles=3, right_candles=3, waves_number=3,resistance_trend=False,support_trend=False,npiv=3):
    # symbol = 'BTC_USDT'
    # read_rsi = True
    # exch = 'Kucoin'
    # tf = '1h'
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
                df, left_candles, right_candles, waves_number, short=False)

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
            #st.dataframe(df)

            fig.add_trace(
                go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
            )
            pointpos_df = pd.DataFrame(
                data=df[~pd.isnull(df['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
            boudry_xs=[df[0:1]['timestamp'].values[0],df[-1:]['timestamp'].values[0]]
            if support_trend:
                down_xs = pointpos_df[pointpos_df['pivot'] == 1]['timestamp']
                down_ys = pointpos_df[pointpos_df['pivot'] == 1]['pointpos']
                m=npiv
                if npiv==0:m=len(down_ys)
                r2_down,trend_down_xs,trend_down_ys=helper.ReturnTrend_From_Comb(helper.Return_Combo(xs=down_xs.values,ys=down_ys.values,n=m,r_min=0.92),bounds=boudry_xs)
                trend_down_xs_time=pd.to_datetime(trend_down_xs,unit='ms')
                fig.add_trace(
                    go.Scatter(x=trend_down_xs_time, y=trend_down_ys, line=dict(
                        color="gray"), name=f'r2_sq(support):{r2_down}'), row=1, col=1
                )                           

            if resistance_trend:
                up_xs = pointpos_df[pointpos_df['pivot'] == 2]['timestamp']
                up_ys = pointpos_df[pointpos_df['pivot'] == 2]['pointpos']
                m=npiv
                if npiv==0:m=len(up_ys)

                combs = list(itertools.combinations(list(zip(up_xs,up_ys)), m))
                sorted_resist_combs = sorted(combs,key=lambda c: helper.r2(c),reverse=True)


                r2_up,trend_up_xs,trend_up_ys=helper.ReturnTrend_From_Comb(helper.Return_Combo(xs=up_xs.values,ys=up_ys.values,n=m,r_min=0.92),bounds=boudry_xs)
                trend_up_xs_time=pd.to_datetime(trend_up_xs,unit='ms')
                fig.add_trace(
                    go.Scatter(x=trend_up_xs_time, y=trend_up_ys, line=dict(
                        color="gray"), name=f'r2_sq(resistance):{r2_up}'), row=1, col=1
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
                df_copy = df.copy()

                df_copy['label'] = np.where(df['ich_moku_color'] > 0, 1, 0)
                df_copy['group'] = df_copy['label'].ne(
                    df_copy['label'].shift()).cumsum()
                df_copy = df_copy.groupby('group')
                dfs = []
                for name, data in df_copy:
                    dfs.append(data)
                for d in dfs:
                    # dot_opacity=np.ones(len(d))
                    # dot_opacity[0]=0

                    fig.add_trace(
                        go.Scatter(x=d['time'], y=d['ich_a'], name='trace', line=dict(color="white", width=0), mode='lines'), row=rownum, col=1,
                    )
                    fig.add_trace(
                        go.Scatter(x=d['time'], y=d['ich_b'], fill='tonexty', fillcolor=fillcol(d['label'].iloc[0]), name='trace', line=dict(color="white", width=0), mode='lines'), row=rownum, col=1
                    )
                for trace in fig['data']:
                    if (trace['name'] == 'trace'):
                        trace['showlegend'] = False

                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_a'], name='span a', line=dict(color="green", width=0.7)), row=rownum, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_b'], name='span b', line=dict(color="red", width=0.7)), row=rownum, col=1
                )

                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_base_line'], name='ichi_base_line', line=dict(color="blue", width=1)), row=rownum, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['ich_conversion_line'], name='ichi_conversion_line', line=dict(color="red", width=1)), row=rownum, col=1
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
                    go.Scatter(x=df['time'], y=df['rsi'], name='rsi', line=dict(width=2, color='#d5dae5')), row=rownum, col=1
                )
                if (entry_signals):
                    dvg_res, px, py, rsi_x, rsi_y = helper.Rsi_Divergence_3(df)
                    if (dvg_res):
                        fig.add_trace(
                            go.Scatter(x=px, y=py, name='divergence on graph', line=dict(width=3, color='#ff6c00')), row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(x=rsi_x, y=rsi_y, name='divergence on rsi', line=dict(width=2, color='#ff6c00')), row=rownum, col=1
                        )
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['rsi_entry_signal'], mode='markers', marker=dict(size=8, symbol="diamond", line=dict(width=2, color=1.5)), name='rsi entry signal'), row=1, col=1
                    )
            if (read_vol):
                rownum += 1
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['volume'], name='Volume'), row=rownum, col=1
                )
            if (read_sma):
                helper.append_sma_2(
                    df, entry_signal=entry_signals, w1=10, w2=50)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_1'], name='sma 10'), row=1, col=1
                )
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['sma_2'], name='sma 50'), row=1, col=1
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
    df0 = df0[-1200:]

    df = df0[:-forecast_out]
    df = df[['time', 'close', 'open', 'high', 'low', 'volume']]
    df['hl_pct'] = (df['high']-df['low'])/df['low'] * 100
    df['pct_change'] = (df['close']-df['open'])/df['low'] * 100
    df = df[['time', 'close', 'volume', 'hl_pct', 'pct_change',
             'rsi_entry_signal', 'pband', 'fi_norm', 'adx_pos_neg']]
    forecast_col = 'close'
    df.fillna(-99999, inplace=True)

    forecast_out = int(math.ceil(0.015*len(df)))
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
              entry_signals=entry_signals_check, entry_signal_mode=entry_signal_mode, left_candles=pivot_candle_left, right_candles=pivot_candle_right,
               waves_number=waves_number,resistance_trend=resistance_trend,support_trend=support_trend,npiv=npiv)


st.sidebar.title("Chart parameters: ")


with st.sidebar:
    limit = st.number_input("Data Limit:", min_value=40, value=280)
    st.write("Pivot Settings:")
    pivot_candle_left = st.number_input("Left Candles:", min_value=2, value=6)
    pivot_candle_right = st.number_input(
        "Right Candles:", min_value=2, value=6)
    resistance_trend=st.checkbox("Overal Resistance Trend",value=False)
    support_trend=st.checkbox("Overal Support Trend",value=False)
    npiv=st.number_input("Number Of Trend Pivots:",min_value=0,value=3)
    st.write('Price Action Settings:')
    waves_number = st.number_input("Number of Waves:", min_value=2, value=2)

    st.write("Indicators")
    ichi_check = st.checkbox("Ichi Moku", value=True)
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
    # ML_check = st.checkbox("ML Predict", value=False)
    # if (ML_check):
    #     forecast_out = st.number_input(
    #         "Forecast Number:", min_value=5, max_value=30, value=20)
    #     if st.button('ML Predict Price'):
    #         if (q.__contains__('symbol') and q.__contains__('tf')):
    #             symbol = q['symbol'][0]
    #             tf = q['tf'][0]
    #             PredictPrice(coin=symbol, tf=tf, forecast_out=forecast_out)

with st.container():
    cols = st.columns([1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1])
    tfs = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    if exch == 'Yahoo':
        tfs = ['5m', '15m', '30m', '60m', '90m', '1d', '1wk']

    for i in range(0, len(tfs)):
        if cols[i].button(tfs[i]):
            tf = tfs[i]
            st.experimental_set_query_params(tf=tf, exch=exch, symbol=symbol)
    if cols[len(tfs)].button('Download Latest'):
        if exch == 'Kucoin':
            if (symbol.lower().__contains__('usdt')):
                mr.ReadKucoinMarket(timeframes=tfs,
                                    local=local, testdata=False, symbol=symbol.replace('_', '/').upper())
        elif exch == 'Yahoo':
            mr.ReadYahooMarket(timeframes=tfs,
                               local=local, testdata=False, symbol=symbol)


DrawTheChart()
