import os , pandas as pd
from pathlib import Path
Base_DIR='/root/trader_webapp/'

def is_consolidating(df,candles=15, percentage=2):
    recent_candles=df[-candles:]
    max_close=recent_candles['close'].max()
    min_close=recent_candles['close'].min()
    threshold=1-(percentage/100)
    if min_close > (max_close * threshold):
        return True
    return False

def is_breaking_out(df,candles=15,percentage=2):
    last_close=df[-1:]['close'].values[0]

    if (is_consolidating(df[:-1],candles=candles,percentage=percentage)):
        if(last_close>df[-(candles+1):-1]['close'].max()):
            return True
    return False

def is_coin_breaking_out(Coin,tf,exchangename='Kucoin', candles=15,percentage=2,relp=False):
    df=None
    rel_dir='Market Data/{}/{}/'.format(exchangename,tf,Coin)
    abs_dir=os.path.join(Base_DIR,rel_dir)
    if(relp):
        abs_dir=rel_dir
    for path in Path(abs_dir).iterdir():
        if(path.name.startswith(Coin.replace('/','_'))):
            df=pd.read_csv(path)
            break
    if(df.size):
        last_close=df[-1:]['close'].values[0]
        if (is_consolidating(df[:-1],candles=candles,percentage=percentage)):
            if(last_close>df[-(candles+1):-1]['close'].max()):
                return True
    return False

def ChackConsolidations(tf,candles,ecxchangeName='Kucoin',percentage=2, relp=False):
    rel_dir='Market Data/{}/{}/'.format(ecxchangeName,tf)
    abs_dir=os.path.join(Base_DIR, rel_dir)
    if(relp):
        abs_dir=rel_dir
    paths = Path(abs_dir).iterdir()
    for path in paths:
        df=pd.read_csv(path)
        if(df.size>100):
            #if(is_consolidating(df,candles=candles,percentage=percentage)):
                #print("{} - {} is Consolidating".format(df['Coin'][0],tf))
            if(is_breaking_out(df,candles=candles,percentage=percentage)):
                print("{} - {} is Breaking Out".format(df['Coin'][0],tf))
                print("Last Close:{}".format(df[-1:]['close'].values[0]))
                print(df)
#ChackConsolidations(tf='4h',candles=15,ecxchangeName='Kucoin', percentage=2,relp=True)
