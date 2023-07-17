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
start_test=0
end_test=400

st.sidebar.title("Settings: ")
with st.sidebar:
    strategy=st.selectbox("Choose Strategy:",['SMA','Analysis'])
    match strategy:
        case 'SMA':
            take_proft_opt=st.radio('Taking Profit Method:',['By Strategy','Manually'])
            if(take_proft_opt=='Manually'):
                takeprofit=st.number_input('Take Profit (%):',value=7,min_value=1)
            else:
                takeprofit=0
            stoploss=st.number_input('Stop Loss (%):',value=7,min_value=1)
        case 'Analysis':
            candles_back=st.number_input("Candles:",min_value=1,max_value=320,value=50)
        # case 'ML Prediction':
        #     candles_back=st.number_input("Candles Back:",min_value=1,max_value=320,value=300)
        #     stoploss=st.number_input('Stop Loss (%):',value=2,min_value=1)
q = st.experimental_get_query_params()
symbol='BTC_USDT'
tf='1h'
if (q.__contains__('symbol')):
    symbol = q['symbol'][0]
if (q.__contains__('tf')):
    tf=q['tf'][0]
exch='Kucoin'
init_df=helper.GetData(tf,symbol,exch)



def Run_sma_Strategy(x)-> tm.TradingEnv:
    fee=0.99875
    env=tm.TradingEnv(balance_amount=100,balance_unit='USDT',trading_fee_multiplier=fee)

    df=pd.DataFrame(data=init_df).copy()

    buying=False

    helper.append_sma(df,entry_signal=True,entry_signal_mode='All')
    df=df.loc[df['sma_30'].isna()==False].reset_index()
    profit=x[0]
    stoploss=x[1]
    entry_offset=0
    exit_offset=1
    df_crop=df[entry_offset:-exit_offset].reset_index()
    transaction=None
    for i in range(0,len(df_crop)):
        close_price = df_crop.loc[i,"close"]
        low_price = df_crop.loc[i,"low"]
        high_price = df_crop.loc[i,"high"]
        sma_5 = df_crop.loc[i,"sma_5"]
        sma_10 = df_crop.loc[i,"sma_10"]
        sma_30 = df_crop.loc[i,"sma_30"]
        # forward=df.loc[df['timestamp']>df.loc[i,'timestamp']].reset_index()
        time = df_crop.loc[i,"time"]
        open_price = df_crop.loc[i,"open"]
        if(buying==False):
            if not pd.isna(df_crop.loc[i,"sma_entry_signal"]):
                env.buy(symbol==symbol,buy_price=open_price,time=time)
                transaction=tm.Transaction(coin=symbol,buy_time=time,buy_price=open_price,signal_time=time)
                buying=True
            else:
                continue
        else:
            if(low_price<(1-0.01*stoploss)*transaction.Buy_price): # stopp loss
                env.sell(sell_price=(1-0.01*stoploss)*transaction.Buy_price,time=time,transaction=transaction)
                transaction=None
                buying=False
                continue
            if(profit>0):
                if(high_price>(1+0.01*profit)*transaction.Buy_price): # take profit
                    env.sell(sell_price=(1+0.01*profit)*transaction.Buy_price,time=time,transaction=transaction)
                    transaction=None
                    buying=False
                    continue
            else:
                if(not(pd.isna(sma_30) or pd.isna(sma_10) or pd.isna(sma_5))):
                    if(sma_30> sma_10 and sma_10 > sma_5):
                        env.sell(sell_price=close_price,time=time,transaction=transaction)
                        transaction=None
                        buying=False
                        continue

            if(i==len(df_crop)-1): # last time
                env.sell(sell_price=close_price,time=time,transaction=transaction)
                transaction=None
                buying=False
                continue

# if(len(env.transactions)>0):
            #     lastsell_time=env.transactions[-1].Sell_time
            #     if(df_crop.loc[i,'date']<lastsell_time):continue
    return  env





    # st.text(f"fee:{fee} ; profit:{profit} ; stoploss:{stoploss}")

def DrawAnaylsisChart():
    #candles_back=2
    tfs = ['1d','4h', '1h','15m']
    totalpoints={}
    totalpoints[tf]=[]
    df=helper.GetData(tf=tf,symbol=symbol,exch=exch)
    df_long = df[-ac.Long_Term_Trend_Limit:].reset_index(drop=True)
    df_short = df[-ac.Short_Term_Trend_Limit:].reset_index(drop=True)
    df_long= pivot_helper.find_pivots(
    df_long, ac.Long_Term_Candles, ac.Long_Term_Candles, ac.PA_Power_Calc_Waves, short=True)
    df_short= pivot_helper.find_pivots(
    df_short, ac.Short_Term_Candles, ac.Short_Term_Candles, ac.PA_Power_Calc_Waves, short=True)
    fig=chh.DrawCandleSticks(df_short,df_short,both=False,symbol=symbol)
    index = tfs.index(tf)
    filtered_tfs = tfs[index-1:index+1] if index > 0 else [tfs[0]]
    # [t for t in tfs if t=='4h' or t=='1h']
    # for t in tfs:
    df_short[f'{tf} point']=0
    df_short[f'{tf} Buy']=np.nan
    df_short[f'{tf} Sell']=np.nan

    for i in range(candles_back,0,-1):
        # df_short.iloc[len(df_short)-i, df_short.columns.get_loc(f'{tf} point')]=3

        analyzer=a.Analyzer()
        analyzer.init_data(tfs=filtered_tfs,exch=exch,symbol=symbol,trend_limit_long=ac.Long_Term_Trend_Limit,
                            trend_limit_short=ac.Short_Term_Trend_Limit,long_term_pivot_candles=ac.Long_Term_Candles,
                            short_term_pivot_candles=ac.Short_Term_Candles,
                            pvt_trend_number=ac.Pivot_Trend_Number,waves_number=ac.PA_Power_Calc_Waves,candles_back=i-1)
   
        dict_buy_sell=analyzer.buy_sell(tf)
        buy_pars=s.Parametrs()
        sell_pars=s.Parametrs()
        buy_pars=dict_buy_sell['buy']
        sell_pars=dict_buy_sell['sell']
        df_short.iloc[len(df_short)-i, df_short.columns.get_loc(f'{tf} point')]=buy_pars.calc_points()-sell_pars.calc_points()
        
        this_row=df_short.iloc[len(df_short)-i]
        df0=df_short[["close","open","high","low","volume"]].tail(1).reset_index(drop=True)
        features_dict=analyzer.features(tf=tf)
        df_features = pd.DataFrame.from_dict(features_dict,orient='columns').reset_index(drop=True)
        df_input=pd.concat([df0,df_features],axis=1)
        targets=['buy','sell']
        for target in targets:
            models=ML_2.Predict(input=df_input,exch=exch,tf=tf,symbol=symbol,target=f'{target}')
            if len(models)>0:
                tree_model=next(m for m in models if m["name"]=='Random Forest')
                if tree_model["prediction"][0]==1:
                    df_short.iloc[len(df_short)-i, df_short.columns.get_loc(f'{tf} {target.capitalize()}')]=this_row.close
                


    chh.AppendLineChart(fig=fig,xs=df_short['time'],ys=df_short[f'{tf} point'],col=1,row=2)
    chh.AppendPointChart(fig=fig,xs=df_short['time'],ys=df_short[f'{tf} Buy'],col=1,row=1,name='Buy',color='green')
    chh.AppendPointChart(fig=fig,xs=df_short['time'],ys=df_short[f'{tf} Sell'],col=1,row=1,name='Sell',color='red')
    fig.update_layout(xaxis_rangeslider_visible=False,
                        height=450)
    st.plotly_chart(fig, use_container_width=True)

#DrawAnaylsisChart()
st.title(f"{strategy} Strategy")            
if st.button('Run Strategy'):
    if strategy=='SMA':
        x=[takeprofit,stoploss]
        env=Run_sma_Strategy(x)
        st.text(f"Balance: {env.balance_amount} unit:{env.balance_unit}")
        st.text(f"Total Profit: {round(env.balance_amount-100,2)} %")
        st.dataframe(env.dataframe())
    if strategy=='Analysis':
        DrawAnaylsisChart()
    


