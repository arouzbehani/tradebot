from datetime import datetime
import pandas as pd
import GLOBAL
from pathlib import Path
import numpy as np

# Input GMT time in the format "01.01.2022 00:00:00.000"
def to_timestamp(gmt):
    # Define the format of the input string
    format_string = "%d.%m.%Y %H:%M:%S.%f"

    # Convert the GMT time string to a datetime object
    gmt_datetime = datetime.strptime(gmt, format_string)

    # Convert the datetime object to a timestamp (UNIX timestamp)
    timestamp =round(gmt_datetime.timestamp()*1000)
    return timestamp
symbol='AUDCAD'
tf='1h'
rel_dir = "Market Data/{}/{}/".format('Forex', tf, symbol)
    # rel_dir='Market Data/{}/{}/'.format(exch,tf,symbol)
abs_dir = GLOBAL.ABSOLUTE(rel_dir, True)
df=None
path_df=''
for path in Path(abs_dir).iterdir():
    if path.name.lower().startswith(symbol.lower()):
        df = pd.read_csv(path)
        path_df=path
        break
df['timestamp']=df['Gmt time'].map(to_timestamp)
df['Symbol']=symbol
df.rename(columns={'Open': 'open', 'High': 'high','Low':'low','Close':'close','Volume':'volume'}, inplace=True)
df=df[df['volume']>0].reset_index(drop=True)
df.to_csv(path,index=False, sep=',', mode='w')

print (df)

