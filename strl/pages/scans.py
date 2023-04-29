import streamlit as st
import os , gc , GLOBAL
import pandas  as pd
from pathlib import Path
from streamlit.components.v1 import html
import streamlit.components.v1 as components

local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True

def makelink(c,streaml,exch):
    symbol=c.replace('/','_')
    return (f'''{streaml}analysis?symbol={symbol}&exch={exch}''')
def make_clickablez(name,streaml,exch,tf):
    url='{}?chartsymbol={}&exch={}&tf={}'.format(streaml,name.replace('/','_'),exch,tf)
    return '{}" rel="noopener noreferrer" target="_blank">{}'.format(url,name)
def make_clickable(url,name):
    return  (f'''<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>''')

def GetDF(exch):
    rel_path = 'Scans/{}/'.format(exch)
    abs_dir =GLOBAL.ABSOLUTE(rel_path,local)
    if(os.path.exists(abs_dir)):
        paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
        if(paths.__len__()>0):
            path=paths[-1:][0]

            df=pd.read_csv(path)
    return df,path.name.split('__')[0].replace('_','/') + ' ' + path.name.split('__')[1].replace('_',':').split('.')[0]
def sq_match(row,sq):
    words=sq.split(',')
    res=[]
    for w in words:
        for item in row.items():
            if(str(row[item[0]]).lower().__contains__(w.strip().lower())):
                res.append(1)
    if(len(res)>=len(words)):
        return 1
    return 0
def table(df,exchange='Kucoin',sq='sma entry'):
    # streaml='http://localhost:8501/'
    streaml='http://trader.baharsoft.com:8100/'

    pretty = df[['Symbol', '1d point', '4h point','1h point','15m point']]
    pretty['url']=pretty['Symbol'].apply(makelink,streaml=streaml,exch=exchange)
    pretty['Symbol'] = pretty.apply(lambda x: make_clickable(x['url'],x['Symbol']), axis=1)
    # pretty.style
    pretty.__delitem__('url')
    if(sq!=''): 
        all=[]
        pretty['sq']=pretty.apply(lambda row: sq_match(row,sq=sq), axis=1)

        filtered=pretty[pretty['sq'] ==1]
        if(len(filtered)>0):
            all.append(filtered)
            
        if len(all)>0:
            pretty=pd.concat(all).drop_duplicates().sort_index()
        else:
            pretty.drop(pretty.index, inplace=True)

        pretty.__delitem__('sq')
        del all
        gc.collect()
    del df
    gc.collect()
    return pretty

def crypto_scans():
    df,date_time = GetDF(exch='Kucoin')
    sq=st.text_input(label='',placeholder='Serch Symbol Name')
    t=table(df,exchange='Kucoin',sq=sq)
    st.subheader(date_time)
    st.write(t.to_html(escape=False, index=False), unsafe_allow_html=True)
def stocks_scans():
    df,date_time = GetDF(exch='Yahoo')
    sq=st.text_input(label='',placeholder='Serch Symbol Name')
    t=table(df,exchange='Yahoo',sq=sq)
    st.subheader(date_time)
    st.write(t.to_html(escape=False, index=False), unsafe_allow_html=True)
with st.sidebar:
    market=st.selectbox('Market',['Crypto','US Stock','Forex'])

if market=='Crypto':
    crypto_scans()
if market=='US Stock':
    stocks_scans()
