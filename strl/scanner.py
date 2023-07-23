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
import situations

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
                                if np.mean(model["precision_scores"])>=0.8:
                                    message=f'{p} {s} -- {tf} ---- Current Candle: {sit_df.iloc[-1].time} (UTC)' + '\r\n'
                                    message +=f'Analysis Point: {round(point,2)}'+ '\r\n'
                                    message +=f'Possible Trade: {model["deals"]}% , Candles: {model["cn"]} , TP: {model["tp"]}'+ '\r\n'
                                    message +=f'Model: {model["name"]}' + '\r\n'
                                    message +=f'Mean Recall Score:{round(np.mean(model["recall_scores"]),2)}'+ '\r\n'
                                    message +=f'Mean Accuracy Score:{round(np.mean(model["accuracy_scores"]),2)}'+ '\r\n'
                                    message +=f'Mean Precision Score:{round(np.mean(model["precision_scores"]),2)}'
                                    print(message)
                                    asyncio.run(tlgm.main("-1001982135624",message))
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
    ML_Scan()