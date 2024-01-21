import streamlit as st
import helper
import pivot_helper
import pandas as pd
import trader_model as tm
import numpy as np
import analaysis_constants as ac
import analyzer as a
import situations as s
import chart_helper as chh
import ML_2
import matplotlib.pyplot as plt
from scipy.stats import norm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_profit_dist(env_df):


    # Assuming env_df is your DataFrame
    # Replace 'Profit' with the actual column name if it's different
    profit_column = env_df['Profit']

    # Calculate mean and standard deviation
    mean_profit = profit_column.mean()
    std_dev_profit = profit_column.std()

    # Generate data points for the normal distribution PDF
    min_value = profit_column.min()
    max_value = profit_column.max()
    x = np.linspace(min_value, max_value, 1000)
    pdf = norm.pdf(x, mean_profit, std_dev_profit)

    # Plot the histogram of 'Profit'
    plt.hist(profit_column, bins=30, density=True, alpha=0.7, color='blue', label='Histogram')

    # Plot the PDF of the normal distribution
    plt.plot(x, pdf, color='red', label='Normal Distribution')

    # Add labels and a legend
    plt.xlabel('Profit')
    plt.ylabel('Probability Density')
    plt.title('Normal Distribution of Profit')
    plt.legend()

    # Show the plot
    plt.show()

st.set_page_config(layout="wide")
st.markdown(
    """

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
        """,
    unsafe_allow_html=True,
)
start_test = 0
end_test = 400
takeprofit=0
stoploss=0
st.sidebar.title("Settings: ")
with st.sidebar:
    fee=st.number_input("Transaction Fee (%):",value=0.125,min_value=0.01,max_value=100.0)
    leverage=st.number_input("Leverage:",value=10,max_value=1000,min_value=1)
    tpsl_opt=st.radio("TP/SL Method:",['By Strategy','Fixed'])
    if tpsl_opt=='Fixed':
        stoploss_percent = st.number_input("Stop Loss (%):", value=2.0, min_value=0.05)
        tpsl_ratio=st.number_input("TPSL Ratio:",value=1.5,min_value=0.1)
    else:
        stoploss=0
        tpsl_ratio=0

    strategy = st.selectbox("Choose Strategy:", ["EMA","Bollinger Bands (Single EMA)","Bollinger Bands (Double EMA)","Point Analysis","ML Analysis"])
    


    match strategy:
        case "EMA":
            ema_win1=st.number_input("EMA 1:",5)
            ema_win2=st.number_input("EMA 2:",10)
            ema_win3=st.number_input("EMA 3:",30)
            ema_sl_coef=st.number_input("SL Coef.:",value=2.0,min_value=0.1)
            ema_tpsl_ratio=st.number_input("TPLS Ratio:",value=1.5,min_value=0.1)

        case "Bollinger Bands (Single EMA)":
            bb_ema=st.number_input("EMA:",value=170 , min_value=5)
            bb_window=st.number_input("Window",value=15,min_value=5)
            bb_window_dev=st.number_input("Win Dev.",value=1.5,min_value=0.1)
            bb_atr_win=st.number_input("ATR Window:",value=7,min_value=1)
            bb_sl_coef=st.number_input("SL Coef.:",value=1.1,min_value=0.1)
            bb_tpsl_ratio=st.number_input("TPLS Ratio:",value=1.5,min_value=0.1)

        case "Bollinger Bands (Double EMA)":
            bb_ema_1=st.number_input("EMA 1:",value=30 , min_value=5)
            bb_ema_2=st.number_input("EMA 2:",value=50 , min_value=5)
            bb_window=st.number_input("Window",value=15,min_value=5)
            bb_window_dev=st.number_input("Win Dev.",value=1.5,min_value=0.1)
            bb_atr_win=st.number_input("ATR Window:",value=7,min_value=1)
            bb_sl_coef=st.number_input("SL Coef.:",value=1.1,min_value=0.1)
            bb_tpsl_ratio=st.number_input("TPLS Ratio:",value=1.5,min_value=0.1)

        case "Point Analysis":
            candles_back = st.number_input(
                "Candles:", min_value=1, max_value=320, value=50
            )

        case "ML Analysis":
            candles_back = st.number_input(
                "Candles:", min_value=1, max_value=320, value=50
            )            
        # case 'ML Prediction':
        #     candles_back=st.number_input("Candles Back:",min_value=1,max_value=320,value=300)
        #     stoploss=st.number_input('Stop Loss (%):',value=2,min_value=1)
q = st.experimental_get_query_params()
symbol = None
tf = None
exch = None
# symbol = 'EUR_USD'
# tf = '5min'
# exch = 'Forex'
q = st.experimental_get_query_params()
if q.__contains__("symbol"):
    symbol = q["symbol"][0]
if q.__contains__("tf"):
    tf = q["tf"][0]
if q.__contains__("exch"):
    exch = q["exch"][0]
init_df = helper.GetData(tf, symbol, exch)


# strategy='EMA'
# ema_win1=5
# ema_win2=10
# ema_win3=30
# ema_sl_coef=2
# ema_tpsl_ratio=1.5

# strategy='Bollinger Bands (Double EMA)'
# bb_window=15
# bb_window_dev=1.5
# bb_atr_win=7
# bb_sl_coef=1.1
# bb_tpsl_ratio=1.5
# bb_ema_1=30
# bb_ema_2=50 


# strategy='Bollinger Bands (Single EMA)'
# bb_window=15
# bb_window_dev=1.5
# bb_atr_win=7
# bb_sl_coef=1.1
# bb_tpsl_ratio=1.5
# bb_ema=170

# fee=0.00125
# leverage=100

def Run_Strategy() -> tm.TradingEnv:
    env = tm.TradingEnv(
        balance_amount=100, balance_unit="USDT", trading_fee_multiplier=fee*0.01,leverage=leverage
    )

    df = pd.DataFrame(data=init_df).copy()

    buying = False
    match strategy:
        case "EMA":
            long_signal_header='ema_entry_signal'
            short_signal_header='ema_exit_signal'
            helper.append_ema(df, entry_signal=True, entry_signal_mode="All", exit_signal=True, win1=ema_win1,win2=ema_win2,win3=ema_win3)
            df = df.loc[df[f"ema_{ema_win3}"].isna() == False].reset_index()
        case "Bollinger Bands (Single EMA)":
            long_signal_header='bb_long_signal'
            short_signal_header='bb_short_signal'            
            helper.append_ema_W(df,window=bb_ema)
            helper.append_bb_v2(df,win=bb_window,win_dev=bb_window_dev)
            helper.append_atr(df,win=bb_atr_win)
            df = df.loc[df[f"ema_{bb_ema}"].isna() == False].reset_index()

        case "Bollinger Bands (Double EMA)":
            long_signal_header='bb_long_signal'
            short_signal_header='bb_short_signal'            
            helper.append_ema_W(df,window=bb_ema_1)
            helper.append_ema_W(df,window=bb_ema_2)
            helper.append_atr(df,win=bb_atr_win)
            helper.append_bb_v3(df,win=bb_window,win_dev=bb_window_dev)
            df = df.loc[df[f"ema_{bb_ema_2}"].isna() == False].reset_index()

    entry_offset = -10000
    exit_offset = -1
    df_crop = df[entry_offset:exit_offset].reset_index()
    transaction = None
    stoploss=0
    profit=0
    trade_mode='spot'
    df_crop['balance']=0
    df_crop.loc[0,'balance']=env.balance_amount
    for i in range(0, len(df_crop)):
        if i>0:
            if df_crop.loc[i-1,'balance']>0:
                df_crop.loc[i,'balance']=df_crop.loc[i-1,'balance']
        close_price = df_crop.loc[i, "close"]       
        low_price = df_crop.loc[i, "low"]
        high_price = df_crop.loc[i, "high"]
        time = df_crop.loc[i, "time"]
        if tpsl_opt=='By Strategy':
            match strategy:
                case "EMA":
                    stoploss=ema_sl_coef*(high_price-low_price)
                    profit=tpsl_ratio*stoploss
                case "Bollinger Bands (Single EMA)":
                    atr = df_crop.loc[i, "atr"]
                    stoploss=bb_sl_coef*atr
                case "Bollinger Bands (Double EMA)":
                    atr = df_crop.loc[i, "atr"]
                    stoploss=bb_sl_coef*atr
                    profit=bb_tpsl_ratio*stoploss                   
        else:
            stoploss=stoploss_percent*0.01*close_price
            profit=stoploss*tpsl_ratio

        if buying == False:
            if not pd.isna(df_crop.loc[i, f"{long_signal_header}"]):           
                env.buy(symbol == symbol, trade_mode='long', buy_price=close_price, time=time)
                transaction = tm.Transaction(
                    coin=symbol, trade_mode='long', buy_time=time, buy_price=close_price, signal_time=time,sl=close_price-stoploss,tp=close_price+profit
                )
                trade_mode='long'
                buying = True
                continue
            elif not pd.isna(df_crop.loc[i, f"{short_signal_header}"]):     
                env.buy(symbol == symbol, trade_mode='short', buy_price=close_price, time=time)
                transaction = tm.Transaction(
                    coin=symbol, trade_mode='short', buy_time=time, buy_price=close_price, signal_time=time,sl=close_price+stoploss,tp=close_price-profit
                )
                trade_mode='short'
                buying = True
                continue
        else:
            if (trade_mode=='long' and low_price < transaction.SL) or (trade_mode=='short' and high_price >  transaction.SL):  # stopp loss
                transaction.Sell_price=transaction.SL
                transaction.Sell_time=time
                df_crop.loc[i, "balance"]=env.sell(transaction=transaction)
                transaction = None
                buying = False
                continue
            if profit > 0:
                if (trade_mode=='long' and high_price > close_price+ profit) or (trade_mode=='short' and low_price < profit) : # take profit
                    transaction.Sell_price=transaction.TP
                    transaction.Sell_time=time
                    df_crop.loc[i, "balance"]=env.sell(transaction=transaction)
                    transaction = None
                    buying = False
                    continue        
            else:
                if (trade_mode=='long' and not pd.isna(df_crop.loc[i, f"{short_signal_header}"])) or \
                   (trade_mode=='short' and not pd.isna(df_crop.loc[i, f"{long_signal_header}"])):
                    if (trade_mode=='long'  and close_price>transaction.Buy_price*(1+fee*0.01) or (trade_mode=='short'  and close_price<transaction.Buy_price*(1-fee*0.01))):
                        transaction.Sell_price=close_price
                        transaction.Sell_time=time                    
                        df_crop.loc[i, "balance"]=env.sell(transaction=transaction)
                        transaction = None
                        buying = False
                        continue    
            if i == len(df_crop) - 1:  # last time
                transaction.Sell_price=close_price
                transaction.Sell_time=time     
                df_crop.loc[i, "balance"]=env.sell(transaction=transaction)
                transaction = None
                buying = False
                continue
        
    if not env == None:
        print(f"Balance: {env.balance_amount} unit:{env.balance_unit}")
        print(f"Total Profit: {round(env.balance_amount-100,2)} %")
        print(f"Total Transactions: {len(env.transactions)}")
        print(f"Win Rate: {round(env.wins/len(env.transactions)*100,2)}")
        env_df=(env.dataframe())
        sorted_env_df=env_df.sort_values(by="Profit", ascending=False)
        print(f'Best Trade:{sorted_env_df.iloc[0].Profit}')
        print(f'Worst Trade:{sorted_env_df.iloc[-1].Profit}')
        # plot_profit_dist(env_df)

    return env,df_crop

    # st.text(f"fee:{fee} ; profit:{profit} ; stoploss:{stoploss}")

def ML_Anaylsis():
    # candles_back=1
    tfs = ["1d", "4h", "1h", "15m"]
    if exch.lower()=='forex':
        tfs = ["1day", "4Hour", "1Hour", "15min"]
    if exch.lower()=='yahoo':
       tfs = ["1d", "90m", "60m", "15m"]

    totalpoints = {}
    totalpoints[tf] = []
    df = helper.GetData(tf=tf, symbol=symbol, exch=exch)
    df_long = df[-ac.Long_Term_Trend_Limit :].reset_index(drop=True)
    df_short = df[-ac.Short_Term_Trend_Limit :].reset_index(drop=True)
    df_long = pivot_helper.find_pivots(
        df_long,
        ac.Long_Term_Candles,
        ac.Long_Term_Candles,
        ac.PA_Power_Calc_Waves,
        short=True,
    )
    df_short = pivot_helper.find_pivots(
        df_short,
        ac.Short_Term_Candles,
        ac.Short_Term_Candles,
        ac.PA_Power_Calc_Waves,
        short=True,
    )
    fig = chh.DrawCandleSticks(df_short, df_short, both=False, symbol=symbol)
    index = tfs.index(tf)
    filtered_tfs = tfs[index - 1 : index + 1] if index > 0 else [tfs[0]]
    # [t for t in tfs if t=='4h' or t=='1h']
    # for t in tfs:
    df_short[f"{tf} point"] = 0
    df_short[f"{tf} Buy"] = np.nan
    df_short[f"{tf} Sell"] = np.nan

    for i in range(candles_back, 0, -1):
        # df_short.iloc[len(df_short)-i, df_short.columns.get_loc(f'{tf} point')]=3

        analyzer = a.Analyzer()
        analyzer.init_data(
            tfs=filtered_tfs,
            exch=exch,
            symbol=symbol,
            trend_limit_long=ac.Long_Term_Trend_Limit,
            trend_limit_short=ac.Short_Term_Trend_Limit,
            long_term_pivot_candles=ac.Long_Term_Candles,
            short_term_pivot_candles=ac.Short_Term_Candles,
            pvt_trend_number=ac.Pivot_Trend_Number,
            waves_number=ac.PA_Power_Calc_Waves,
            th=ac.Threshold / 100,
            candles_back=i - 1,
        )

        dict_buy_sell = analyzer.buy_sell(tf)
        buy_pars = s.Parametrs()
        sell_pars = s.Parametrs()
        buy_pars = dict_buy_sell["buy"]
        sell_pars = dict_buy_sell["sell"]
        df_short.iloc[len(df_short) - i, df_short.columns.get_loc(f"{tf} point")] = (
            buy_pars.calc_points() - sell_pars.calc_points()
        )
        sit = analyzer.situations[tf]
        sit_df = sit.short_term_df
        this_row = df_short.iloc[len(df_short) - i]
        df0 = (
            sit_df[["close", "open", "high", "low", "volume"]]
            .tail(1)
            .reset_index(drop=True)
        )
        features_dict = analyzer.features(tf=tf)
        df_features = pd.DataFrame.from_dict(
            features_dict, orient="columns"
        ).reset_index(drop=True)
        df_input = pd.concat([df0, df_features], axis=1)
        targets = ["buy", "sell"]
        for target in targets:
            models = ML_2.Predict(
                input=df_input, exch=exch, tf=tf, symbol=symbol, target=f"{target}"
            )
            if len(models) > 0:
                tree_model = next(m for m in models if m["name"] == "Random Forest")
                if tree_model["prediction"][0] == 1:
                    df_short.iloc[
                        len(df_short) - i,
                        df_short.columns.get_loc(f"{tf} {target.capitalize()}"),
                    ] = this_row.close

    chh.AppendLineChart(
        fig=fig, xs=df_short["time"], ys=df_short[f"{tf} point"], col=1, row=2
    )
    chh.AppendPointChart(
        fig=fig,
        xs=df_short["time"],
        ys=df_short[f"{tf} Buy"],
        col=1,
        row=1,
        name="Buy",
        color="green",
    )
    chh.AppendPointChart(
        fig=fig,
        xs=df_short["time"],
        ys=df_short[f"{tf} Sell"],
        col=1,
        row=1,
        name="Sell",
        color="red",
    )
    fig.update_layout(xaxis_rangeslider_visible=False, height=450)
    st.plotly_chart(fig, use_container_width=True)


def Point_Anaylsis():
    #candles_back=1
    tfs = ["1d", "4h", "1h", "15m"]
    if exch.lower()=='forex':
        tfs = ["1day", "4Hour", "1Hour", "15min"]
    if exch.lower()=='yahoo':
       tfs = ["1d", "90m", "60m", "15m"]
    
    totalpoints = {}
    totalpoints[tf] = []
    df = helper.GetData(tf=tf, symbol=symbol, exch=exch)
    df_long = df[-ac.Long_Term_Trend_Limit :].reset_index(drop=True)
    df_short = df[-ac.Short_Term_Trend_Limit :].reset_index(drop=True)
    df_long = pivot_helper.find_pivots(
        df_long,
        ac.Long_Term_Candles,
        ac.Long_Term_Candles,
        ac.PA_Power_Calc_Waves,
        short=True,
    )
    df_short = pivot_helper.find_pivots(
        df_short,
        ac.Short_Term_Candles,
        ac.Short_Term_Candles,
        ac.PA_Power_Calc_Waves,
        short=True,
    )
    fig = chh.DrawCandleSticks(df_short, df_short, both=False, symbol=symbol)
    index = tfs.index(tf)
    filtered_tfs = tfs[index - 1 : index + 1] if index > 0 else [tfs[0]]
    # [t for t in tfs if t=='4h' or t=='1h']
    # for t in tfs:
    df_short[f"{tf} total point"] = 0
    pars = s.Parametrs()
    for key in pars.calc_pars():
        df_short[f"{tf} {key} point"] = 0
    for i in range(candles_back, 0, -1):
        # df_short.iloc[len(df_short)-i, df_short.columns.get_loc(f'{tf} point')]=3

        analyzer = a.Analyzer()
        analyzer.init_data(
            tfs=filtered_tfs,
            exch=exch,
            symbol=symbol,
            trend_limit_long=ac.Long_Term_Trend_Limit,
            trend_limit_short=ac.Short_Term_Trend_Limit,
            long_term_pivot_candles=ac.Long_Term_Candles,
            short_term_pivot_candles=ac.Short_Term_Candles,
            pvt_trend_number=ac.Pivot_Trend_Number,
            waves_number=ac.PA_Power_Calc_Waves,
            th=ac.Threshold / 100,
            candles_back=i - 1,
        )

        dict_buy_sell = analyzer.buy_sell(tf)
        buy_pars = s.Parametrs()
        sell_pars = s.Parametrs()
        buy_pars = dict_buy_sell["buy"]
        sell_pars = dict_buy_sell["sell"]
        df_short.iloc[len(df_short) - i, df_short.columns.get_loc(f"{tf} total point")] = (
                    buy_pars.calc_points() - sell_pars.calc_points()
                )        
        for key in pars.calc_pars():
            df_short.iloc[
                len(df_short) - i, df_short.columns.get_loc(f"{tf} {key} point")
            ] = buy_pars.calc_array_points(
                buy_pars.calc_pars()[key]
            ) - sell_pars.calc_array_points(
                sell_pars.calc_pars()[key]
            )

    chh.AppendLineChart(
        fig=fig, xs=df_short["time"], ys=df_short[f"{tf} total point"], col=1, row=2,name='total points' 
    )
    for key in pars.calc_pars():
        chh.AppendLineChart(
            fig=fig, xs=df_short["time"], ys=df_short[f"{tf} {key} point"], col=1, row=2 , name=key
        )

    fig.update_layout(xaxis_rangeslider_visible=False, height=450)
    st.plotly_chart(fig, use_container_width=True)

def PlotResult(crop_df,emas=[]):
    row_heights = [0.6,0.4]
    fig = make_subplots(
    rows=2, cols=1,
    column_widths=[1],
    row_heights=row_heights,
    shared_xaxes=True, vertical_spacing=0.01)

    fig.add_trace(
        go.Candlestick(x=crop_df['time'], open=crop_df['open'], close=crop_df['close'], high=crop_df['high'], low=crop_df['low'], name=symbol.replace('_', '/')), row=1, col=1
    )    

    fig.add_trace(
        go.Scatter(x=crop_df["time"], y=crop_df[f"balance"], name='total balamce', line=dict(width=1), mode='lines'), row=2, col=1
    )    
    if 'upperband' in crop_df.columns:
        fig.add_trace(
            go.Scatter(x=crop_df["time"], y=crop_df["middleband"], name="middle band"),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=crop_df["time"], y=crop_df["upperband"], name="upper band"),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(x=crop_df["time"], y=crop_df["lowerband"], name="lower band"),
            row=1,
            col=1,
        )    
        # fig.add_trace(
        #     go.Scatter(x=crop_df["time"], y=crop_df["bb_width"], name="bb_width"),
        #     row=2,
        #     col=1,
        # )                
    if len(emas)>0:
        for ema in emas:
            fig.add_trace(
                # go.Scatter(x=df["time"], y=df["ema_5"], name="ema 5"), row=1, col=1
                go.Scatter(x=crop_df["time"], y=crop_df[f"ema_{ema}"], name=f"ema_{ema}"), row=1, col=1
            )
        if "ema_entry_signal" in crop_df.columns:
            fig.add_trace(
                go.Scatter(
                    # x=df["time"],
                    x=crop_df["time"],
                    y=crop_df["ema_entry_signal"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        symbol="x-thin",
                        line=dict(width=2, color="green"),
                    ),
                    name="ema long signal",
                )
                )    
        if "ema_exit_signal" in crop_df.columns:
            fig.add_trace(
                go.Scatter(
                    # x=df["time"],
                    x=crop_df["time"],
                    y=crop_df["ema_exit_signal"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        symbol="x-thin",
                        line=dict(width=2, color="red"),
                    ),
                    name="ema short signal",
                )
                )                     
    fig.update_layout(xaxis_rangeslider_visible=False, height=450)
    st.plotly_chart(fig, use_container_width=True)    
#Run_Strategy()

st.title(f"{strategy} Strategy")
if st.button("Run Strategy"):
    if strategy == "EMA" :
        env,crop_df = Run_Strategy()
        PlotResult(crop_df=crop_df,emas=[ema_win1,ema_win2,ema_win3])
    if strategy == "Bollinger Bands (Single EMA)" :
        env,crop_df = Run_Strategy()
        PlotResult(crop_df=crop_df,emas=[bb_ema])
    if strategy ==  "Bollinger Bands (Double EMA)":
        env,crop_df = Run_Strategy()
        PlotResult(crop_df=crop_df,emas=[bb_ema_1,bb_ema_2])                
    if strategy == "Point Analysis":
        Point_Anaylsis()
    if strategy == "ML Analysis":
        ML_Anaylsis()
    if not env == None:
        st.text(f"Balance: {env.balance_amount} unit:{env.balance_unit}")
        st.text(f"Total Profit: {round(env.balance_amount-100,2)} %")
        st.text(f"Total Transactions: {len(env.transactions)}")
        st.text(f"Win Rate: {round(env.wins/len(env.transactions)*100,2)}")
        st.dataframe(env.dataframe())