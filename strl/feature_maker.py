import analyzer as a
import pandas as pd
import datetime
import GLOBAL
import helper
import analaysis_constants as ac
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True
def Make(symbol='FTM_USDT',exch='Kucoin',tf='1d'):
    tfs = ['1d','4h', '1h','15m']
    df=helper.GetData(tf=tf,symbol=symbol,exch=exch)
    candles_back=len(df)-ac.Long_Term_Trend_Limit

    candles_forward=7
    tp=5
    now1 = datetime.datetime.now()
    
    print(datetime.datetime.now())

    for i in range(candles_back,0+candles_forward-1,-1):

        analyzer=a.Analyzer()
        analyzer.init_data(tfs=['1d'],exch=exch,symbol=symbol,trend_limit_long=ac.Long_Term_Trend_Limit,
                            trend_limit_short=ac.Short_Term_Trend_Limit,long_term_pivot_candles=ac.Long_Term_Candles,
                            short_term_pivot_candles=ac.Short_Term_Candles,
                            pvt_trend_number=ac.Pivot_Trend_Number,waves_number=ac.PA_Power_Calc_Waves,candles_back=i)
        features_dict=analyzer.features(tf)
        df_features = pd.DataFrame.from_dict(features_dict,orient='columns')
        df_features_row = df_features.iloc[0]
        for col in df_features.columns:
            df.at[len(df)-i-1, col] = df_features_row[col]

        future_df=df[len(df)-i:len(df)-i+candles_forward]
        future_max_high=future_df['high'].max()
        future_min_low=future_df['low'].min()
        sell_target=0
        buy_target=0
        if future_max_high>=df.iloc[len(df)-i-1].close*(1+tp/100.0): buy_target=1
        if future_min_low<=df.iloc[len(df)-i-1].close*(1-tp/100.0): sell_target=1
        df.at[len(df)-i-1, "buy_target"]=buy_target
        df.at[len(df)-i-1, "sell_target"]=sell_target


    columns_to_drop = ['timestamp', 'Coin','time']
    df=df.drop(columns_to_drop,axis=1)
    df=df.drop(df.index[0:len(df)-candles_back-1]).reset_index(drop=True)
    df=df.drop(df.index[-candles_forward:])
    

    rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(exch,tf, symbol,tp,candles_forward)
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    df.to_csv(abs_path, header=True,
                             index=False, sep=',', mode='w')
    now2 = datetime.datetime.now()
    print(now2-now1)

Make()
