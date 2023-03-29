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
    counter=0
    symbols=mr.GetSymbols(local=local)
    for s in symbols:
        try:
            analyzer=a.Analyzer()
            analyzer.init_data(tfs=['1d','4h','1h','15m'], symbol=s,exch=exch)
            buy_data_4h=analyzer.report_buy('4h')
            buy_data_1h=analyzer.report_buy('1h')
            buy_data_15m=analyzer.report_buy('15m')
            results[s]=[buy_data_4h[5],buy_data_1h[5],buy_data_15m[5]]
            print(f'{s} 1h points: {buy_data_1h[5]} ---- 15m points: {buy_data_15m[5]}')
            # counter +=1
            # if counter>1 : break
        except:
            print(f'Error on {s}')
    df = pd.DataFrame.from_dict(results,orient='index')
    df.columns = ['4h point', '1h point', '15m point']
    df.index.name = 'Symbol'
    df = df.sort_values(by='1h point', ascending=False)
    now = datetime.datetime.now()
    rel_path = "Scans/{}/{}.csv".format(exch, now.strftime("%d_%m_%Y__%H_%M_%S"))
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    df.to_csv(abs_path, header=True,
                             index=True, sep=',', mode='w')
    

