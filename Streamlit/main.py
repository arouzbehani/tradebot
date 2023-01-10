import streamlit as st
import pandas as pd
import helper
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from talibHelper import AllPatterns as alp
Base_DIR = '/root/trader_webapp/'
relp = True
st. set_page_config(layout="wide")
st.markdown("""

        <style>
                .css-1vq4p4l {
                    padding: 2rem 1rem 1.5rem;
                }
               .css-18e3th9 {
                    padding-top: 0rem;
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


q = st.experimental_get_query_params()

if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
    st.title(symbol.replace('_', '-').upper())
    url = 'https://kucoin.com/trade/{}'.format(
        symbol.replace('_', '-').upper())
    link = (st.markdown(f'''
    <a href={url}><button style="background-color:transparent;border:none;text-decoration: underline; color:#21a58a; font-size:large">View {symbol.replace('_','/')} Chart on Kucoin</button></a>
''',
                        unsafe_allow_html=True))

st.sidebar.title("Chart parameters: ")


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


def DrawChart(limit=500, read_patterns=False, read_rsi=False, read_bb=True, read_sma=True, read_ema=False, read_vol=True,read_fi=True, chart_height=800,
              entry_signals=True, exit_signals=False,entry_signal_mode='Uptrend'):
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
        df = helper.GetData(tf, symbol, exch)
        if (df.size):
            limit = limit
            if (len(df) < limit):
                limit = len(df)
            df = df[-limit:]
            if (read_bull_patterns):
                try:
                    patterns_res, ndf = alp(df)
                except:
                    patterns_res = False

            cond = [read_bull_patterns, read_bear_patterns, read_rsi, read_vol,read_fi]
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
            helper.append_adx(df)
            if (entry_signals):
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['adx_signal_marker'], mode='markers', marker=dict(
                        size=8, symbol="star-triangle-up", line=dict(width=2, color=3)), name='adx entry signal')

                )
            if(read_fi):
                rownum +=1
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
                helper.append_bb(df,entry_signal=entry_signals,entry_signal_mode=entry_signal_mode)
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
                helper.append_rsi(df,entry_signal=entry_signals,entry_signal_mode=entry_signal_mode)
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['rsi'], name='rsi'), row=rownum, col=1
                )
                if (entry_signals):
                    fig.add_trace(
                        go.Scatter(x=df['time'], y=df['rsi_entry_signal'], mode='markers', marker=dict(size=8, symbol="star", line=dict(width=2, color=1.5)), name='rsi entry signal'), row=1, col=1
                    )
            if (read_vol):
                rownum += 1
                fig.add_trace(
                    go.Scatter(x=df['time'], y=df['volume'], name='Volume'), row=rownum, col=1
                )
            if (read_sma):
                helper.append_sma(df,entry_signal=entry_signals,entry_signal_mode=entry_signal_mode)
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
                helper.append_ema(df,entry_signal=entry_signals,entry_signal_mode=entry_signal_mode)
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


with st.sidebar:
    limit = st.number_input("Data Limit:", min_value=70, value=300)
    bb_check = st.checkbox("Bollinger bands", value=False)
    rsi_check = st.checkbox("RSI", value=True)
    patterns_check = st.checkbox("Patterns", value=False)
    sma_check = st.checkbox("SMA", value=False)
    ema_check = st.checkbox("EMA", value=True)
    vol_check = st.checkbox("Volume", value=False)
    entry_signals_check = st.checkbox("Entry Signals", value=True)
    if (entry_signals_check):
        entry_signal_names = ['Uptrend', 'All']
        entry_signal_mode = st.radio("Entry Signal Mode", entry_signal_names)
    else:
        entry_signal_mode='None'


DrawChart(limit=limit, read_vol=vol_check, read_bb=bb_check,
          read_ema=ema_check, read_sma=sma_check, read_patterns=patterns_check, read_rsi=rsi_check,
          entry_signals=entry_signals_check,entry_signal_mode=entry_signal_mode)
