import os
import numpy as np
import analyzer as a
import MarketReader as mr
import pandas as pd
import datetime
import GLOBAL
import ML_2
import asyncio
import telegram_messenger as tlgm
import situations , Constants as c
import top_100_crypto
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True

def Scan(exch='Kucoin'):
    results={}
    symbols=mr.GetSymbols(local=local)
    tfs=['1d','4h','1h','15m']
    if exch=='Yahoo':
        tfs=['1d','90m','60m','15m']

    for s in symbols:
        try:
            results[s]=[]
            analyzer=a.Analyzer()
            analyzer.init_data(tfs=tfs, symbol=s,exch=exch)
            str=''
            for x in range(len(tfs)):
                buy_sell_data=analyzer.buy_sell(tfs[x])
                total_point=buy_sell_data['buy'].calc_points()-buy_sell_data['sell'].calc_points()
                results[s].append(total_point)
                str +=f'{s} {tfs[x]} points: {total_point} ---- '
            print(str)
            # counter +=1
            # if counter>1 : break
        except:
            print(f'Error on {s}')
    df = pd.DataFrame.from_dict(results,orient='index')
    df.columns = [tf + ' point' for tf in tfs]
    df.index.name = 'Symbol'
    df = df.sort_values(by='1h point', ascending=False)
    now = datetime.datetime.now()
    rel_path = "Scans/{}/{}.csv".format(exch, now.strftime("%d_%m_%Y__%H_%M_%S"))
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    df.to_csv(abs_path, header=True,
                             index=True, sep=',', mode='w')

def Position_Scan(exch='Kucoin',tf='1h',tfs=['4h','1h','15m']):
    #symbols=mr.GetSymbols(local=local)
    symbols=top_100_crypto.top100
    #symbols=['ATOM_USDT']
    for s in symbols:
        try:
            print(f'Analyzing {s}')
            analyzer=a.Analyzer()
            analyzer.init_data(tfs=tfs, symbol=s,exch=exch)
            sit=analyzer.situations[tf]
            pos_level=analyzer.level_bounce_position(tf=tf)
            pos_fibo=analyzer.fibo_position(tf=tf)
            positions=[pos_level,pos_fibo]
            for pos in positions:
                if len(pos)>0:
                    message=f'Name: {pos["name"]}' + '\r\n'
                    message +=f'{pos["position"]} {s} -- {tf} ---- Current Candle: {sit.short_term_df.iloc[-1].time} (UTC)' + '\r\n'
                    message +=f'Take Profit at: {pos["tp"]} ({pos["tp_percent"]} %)'+ '\r\n'
                    message +=f'Stop Loss at: {pos["sl"]} ({pos["sl_percent"]} %)'+ '\r\n'
                    message +=f'Patterns: {pos["patterns"]}'+ '\r\n'
                    message +=f'http://trader.baharsoft.com:8100/analysis?tf={tf}&exch={exch}&symbol={s}'+ '\r\n'
                    message +=f'https://bingx.com/en-us/futures/forward/{s.replace("_","")}'
                    print(message)
                    asyncio.run(tlgm.main("-1001982135624",message))

        except Exception as e:
           print(f'Error on {s} -- {e}')
def Get_FeaturedSymbols(exch='Kucoin',tf='1h'):
    symbols=[]
    rel_dir=f'Feature_Models/{exch}/{tf}/'
    abs_dir=GLOBAL.ABSOLUTE(rel_dir,local=local)
    for fname in os.listdir(abs_dir):
        if fname.__contains__('_features_'):
            symbols.append(fname.split('_features_')[0])
    return symbols
def ML_Scan(exch='Kucoin',pref_tf=''):
    results={}
    symbols=mr.GetSymbols(local=local)
    tfs=['1d','4h','1h','15m']
    # tfs=['4h']
    if exch=='Yahoo':
        tfs=['1d','90m','60m','15m']
    
    if pref_tf !='':
        tfs=[pref_tf]

    for tf in tfs:
        symbols=Get_FeaturedSymbols(exch=exch,tf=tf)
        # symbols=['SHIB_USDT']
        sell_signals={}
        buy_signals={}
        for s in symbols:
            try:
                print(f'Scanning {s}')
                analyzer=a.Analyzer()
                analyzer.init_data(tfs=[tf], symbol=s,exch=exch)
                sit=analyzer.situations[tf]
                sit_df=sit.short_term_df
                dict_buy_sell=analyzer.buy_sell(tf)
                buy_pars=situations.Parametrs()
                sell_pars=situations.Parametrs()
                buy_pars=dict_buy_sell['buy']
                sell_pars=dict_buy_sell['sell']
                point=buy_pars.calc_points()-sell_pars.calc_points()
                df0=sit_df[["close","open","high","low","volume"]].tail(1).reset_index(drop=True)
                features_dict=analyzer.features(tf=tf)
                df_features = pd.DataFrame.from_dict(features_dict,orient='columns').reset_index(drop=True)
                df_input=pd.concat([df0,df_features],axis=1)
                predict={'buy':{1:'BUY',0:'Nothing'},
                        'sell':{1:'SELL',0:'Nothing'}}
                for target in ['buy','sell']:
                    models=ML_2.Predict(input=df_input,exch=exch,tf=tf,symbol=s,target=f'{target}')
                    if len(models)>0:
                        for model in models:
                            p=predict[target][model["prediction"][0]]
                            if p=='SELL' or p=='BUY' or point>=6.0 or point <=-6:
                                precision=np.mean(model["precision_scores"])
                                if p=='SELL' and np.mean(model["precision_scores"])>=0.75:
                                    sell_signals[s]={'point':point ,'message':f'{p} {s} -- {tf} ---- point: {point} --- precision:{precision}'}
                                if p=='BUY' and np.mean(model["precision_scores"])>=0.75:
                                    buy_signals[s]={'point':point ,'message':f'{p} {s} -- {tf} ---- point: {point} --- precision:{precision}'}                                     
                                if np.mean(model["precision_scores"])>=0.8:
                                    message=f'{p} {s} -- {tf} ---- Current Candle: {sit_df.iloc[-1].time} (UTC)' + '\r\n'
                                    message +=f'Analysis Point: {round(point,2)}'+ '\r\n'
                                    message +=f'Possible Trade: {model["deals"]}% , Candles: {model["cn"]} , TP: {model["tp"]}'+ '\r\n'
                                    message +=f'Model: {model["name"]}' + '\r\n'
                                    message +=f'Mean Recall Score:{round(np.mean(model["recall_scores"]),2)}'+ '\r\n'
                                    message +=f'Mean Accuracy Score:{round(np.mean(model["accuracy_scores"]),2)}'+ '\r\n'
                                    message +=f'Mean Precision Score:{round(np.mean(model["precision_scores"]),2)}'+ '\r\n'
                                    message +=f'http://trader.baharsoft.com:8100/analysis?tf={tf}&exch={exch}&symbol={s}'
                                    print(message)
                                    asyncio.run(tlgm.main("-1001982135624",message))
                for sig in buy_signals:
                    message=''
            except Exception as e:
                 print(f'Error on {s} --- {e}')
    # df = pd.DataFrame.from_dict(results,orient='index')
    # df.columns = [tf + ' point' for tf in tfs]
    # df.index.name = 'Symbol'
    # df = df.sort_values(by='1h point', ascending=False)
    # now = datetime.datetime.now()
    # rel_path = "Scans/{}/{}.csv".format(exch, now.strftime("%d_%m_%Y__%H_%M_%S"))
    # abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    # df.to_csv(abs_path, header=True,
    #                          index=True, sep=',', mode='w')
    
if __name__ == "__main__":
    Position_Scan()