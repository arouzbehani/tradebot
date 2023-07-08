from numpy import arange
import analyzer as a
import pandas as pd
import datetime
import GLOBAL
import helper
import analaysis_constants as ac
import gc , os

local = True
try:
    import subprocess

    interface = "eth0"
    ip = (
        subprocess.check_output(
            "ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True
        )
        .decode()
        .strip()
    )
    local = ip != GLOBAL.SERVER_IP
except:
    local = True

def get_tfs(tf, tfs):
    tfs_2 = []
    for i, t in enumerate(tfs):
        if t == tf:
            if i > 0:
                tfs_2.append(tfs[i - 1])
            tfs_2.append(t)
            break
    return tfs_2
def Find_Optimum_TP(closes,highs,lows,max_cn=13):
    max_buy=0
    max_sell=0    
    tp_buy=0.01  
    tp_sell=0.01
    cn_buy=1
    cn_sell=1
    for cn in range(1,max_cn+1):
        candles_forward=cn
        for tp in arange(0.5,30,0.1):
            buys=0
            sells=0
            for i in range(len(closes)-candles_forward-1):
                this_close=closes[i]
                future_max_high=highs[i+1:i+candles_forward+1].max()
                future_min_low=lows[i+1:i+candles_forward+1].min()
                if future_max_high >= this_close * (1 + tp / 100.0) and future_min_low>=this_close * (1 - tp / 200.0):
                    buys += 1
                if future_min_low <= this_close * (1 - tp / 100.0) and future_max_high<=this_close * (1 + tp / 200.0):
                    sells += 1
            if buys>=max_buy:
                max_buy=buys
                tp_buy=tp
                cn_buy=cn
            if sells>=max_sell:
                max_sell=sells
                tp_sell=tp
                cn_sell=cn
    return round(tp_buy,2),round(tp_sell,2),round(max_buy/len(highs)*100),round(max_sell/len(highs)*100),cn_buy,cn_sell


def Make(
    symbol="FTM_USDT",
    exch="Kucoin",
    tf="1d",
    clean_timestamp=True,
    candles_back=-1,
    extend=False
):
    tfs = ["1d", "4h", "1h", "15m"]
    df = helper.GetData(tf=tf, symbol=symbol, exch=exch)
    if candles_back < 0:
        candles_back = len(df) - ac.Long_Term_Trend_Limit
    else:
        if candles_back > len(df) - ac.Long_Term_Trend_Limit:
            candles_back = len(df) - ac.Long_Term_Trend_Limit
    now1 = datetime.datetime.now()

    print(datetime.datetime.now())
    df_tp=df[len(df)-ac.Long_Term_Trend_Limit-candles_back:len(df)].reset_index(drop=True)
    tp_buy,tp_sell,max_buy,max_sell,cn_buy,cn_sell=Find_Optimum_TP(df_tp['close'].values,df_tp['high'].values,df_tp['low'].values,max_cn=13)
    tps=[tp_buy,tp_sell]
    cns=[cn_buy,cn_sell]
    target_titles=['buy_target','sell_target']
    for i in range(candles_back, 0 + max(cns) - 1, -1):
        analyzer = a.Analyzer()
        analyzer.init_data(
            tfs=[tf],#get_tfs(tf=tf,tfs=tfs),
            exch=exch,
            symbol=symbol,
            trend_limit_long=ac.Long_Term_Trend_Limit,
            trend_limit_short=ac.Short_Term_Trend_Limit,
            long_term_pivot_candles=ac.Long_Term_Candles,
            short_term_pivot_candles=ac.Short_Term_Candles,
            pvt_trend_number=ac.Pivot_Trend_Number,
            waves_number=ac.PA_Power_Calc_Waves,
            candles_back=i,
        )
        features_dict = analyzer.features(tf)
        df_features = pd.DataFrame.from_dict(features_dict, orient="columns")
        df_features_row = df_features.iloc[0]
        for col in df_features.columns:
            df.at[len(df) - i - 1, col] = df_features_row[col]
        for k in range(2):
            candles_forward=cns[k]
            future_df = df[len(df) - i : len(df) - i + candles_forward]
            future_max_high = future_df["high"].max()
            future_min_low = future_df["low"].min()
            target = 0
            this_close=df.iloc[len(df) - i - 1].close
            if k==0: # buy_target
                if future_max_high >= this_close * (1 + tps[k] / 100.0) and future_min_low>=this_close * (1 - tps[k] / 200.0):
                    target = 1
            else: # sell_target
                if future_min_low <= this_close * (1 - tps[k] / 100.0) and future_max_high<=this_close * (1 + tps[k] / 200.0):
                    target = 1
            df.at[len(df) - i - 1, target_titles[k]] = target
        del analyzer
        del df_features
        del future_df
        del features_dict
        gc.collect()
        print(f"candle {i}")
    del df_tp
    gc.collect()
    columns_to_drop = ["timestamp", "Coin", "time"]
    if not clean_timestamp:
        columns_to_drop = ["Coin"]

    df = df.drop(columns_to_drop, axis=1)
    df = df.drop(df.index[0 : len(df) - candles_back - 1]).reset_index(drop=True)
    df = df.drop(df.index[-max(cns):])

    rel_path = "Feature_Models/{}/{}/{}_features_tpbuy_{}_tpsell_{}_buys_{}_sells_{}_cnbuy_{}_cnsell_{}.csv".format(
        exch, tf, symbol, tp_buy,tp_sell,max_buy,max_sell, cn_buy,cn_sell
    )
    abs_path = GLOBAL.ABSOLUTE(rel_path, local=local)
    mode="w"
    header=True
    if extend: 
        mode="a" 
        header=False
    
    df.to_csv(abs_path, header=header, index=False, sep=",", mode=mode)
    now2 = datetime.datetime.now()
    print(now2 - now1)

def Extend(
    symbol="FTM_USDT",
    exch="Kucoin",
    tf="1d",
    candles_forward=7,
    clean_timestamp=False,
    tp=5):
        tfs = ["1d", "4h", "1h", "15m"]
        df = helper.GetData(tf=tf, symbol=symbol, exch=exch)
        rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(
            exch, tf, symbol, tp, candles_forward
        )
        abs_path = GLOBAL.ABSOLUTE(rel_path, local=local)
        if os.path.exists(abs_path):
            df_features=pd.read_csv(abs_path)
            last_timestamp=df_features.iloc[-1].timestamp
            index = df[df['timestamp'] == last_timestamp].index.item()
            subset_df = df.iloc[index+1:]
            candles_back=len(subset_df)
            Make(symbol=symbol,exch=exch,tf=tf,
                 candles_back=candles_back-1,
                 candles_forward=candles_forward,
                 clean_timestamp=clean_timestamp,
                 tp=tp,extend=True)

def Make_Features(extend=False):
    tfs = ["1d", "4h", "1h", "15m"]
    tfs = ["1h", "4h"]
    symbols = ["BNB_USDT","TRX_USDT","FTM_USDT", "ADA_USDT", "MATIC_USDT", "BTC_USDT","ETH_USDT"]
    #symbols = ["TRX_USDT"]
    for tf in tfs:
        for s in symbols:
            if not extend:
                Make(
                symbol=s,
                tf=tf,
                candles_back=3500,
                clean_timestamp=False,
                extend=False)
            else:
                Extend(
                    symbol=s,
                    tf=tf,
                    clean_timestamp=False,
                    tp=ac.ml_const[tf][1],
                    candles_forward=ac.ml_const[tf][0]
                )
Make_Features(extend=False)