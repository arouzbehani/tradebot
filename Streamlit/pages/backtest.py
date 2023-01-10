import streamlit as st
import helper
import pandas as pd
import trader_model as tm
import numpy as np

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
    strategy=st.selectbox("Choose Strategy:",['sma','ema'])
    match strategy:
        case 'sma':
            take_proft_opt=st.radio('Taking Profit Method:',['By Strategy','Manually'])
            if(take_proft_opt=='Manually'):
                takeprofit=st.number_input('Take Profit (%):',value=7,min_value=1)
            else:
                takeprofit=0
            stoploss=st.number_input('Stop Loss (%):',value=7,min_value=1)

q = st.experimental_get_query_params()
coin='BTC_USDT'
tf='1h'
if (q.__contains__('symbol')):
    coin = q['symbol'][0]
if (q.__contains__('tf')):
    tf=q['tf'][0]
exch='Kucoin'
init_df=helper.GetData(tf,coin,exch)

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
                env.buy(symbol=coin,buy_price=open_price,time=time)
                transaction=tm.Transaction(coin=coin,buy_time=time,buy_price=open_price,signal_time=time)
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
st.title(f"{strategy} Strategy")            
if st.button('Run sma Strategy'):
    x=[takeprofit,stoploss]
    env=Run_sma_Strategy(x)
    st.text(f"Balance: {env.balance_amount} unit:{env.balance_unit}")
    st.text(f"Total Profit: {round(env.balance_amount-100,2)} %")
    st.dataframe(env.dataframe())


# main.DrawChart(limit=500, read_vol=False, read_bb=False,
#           read_ema=False, read_sma=True, read_patterns=False, read_rsi=False,
#           entry_signals=True,entry_signal_mode='All')
