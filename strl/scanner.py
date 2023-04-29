import analyzer as a
import MarketReader as mr
import pandas as pd
import datetime
import GLOBAL
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
    

