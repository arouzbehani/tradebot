import streamlit as st
import os , gc , GLOBAL
import pandas  as pd
from pathlib import Path
from streamlit.components.v1 import html
import streamlit.components.v1 as components

local =False

def makelink(c,streaml,exch,tf):
    symbol=c.replace('/','_')
    return (f'''{streaml}chart?symbol={symbol}&exch={exch}&tf={tf}''')
def make_clickablez(name,streaml,exch,tf):
    url='{}?chartsymbol={}&exch={}&tf={}'.format(streaml,name.replace('/','_'),exch,tf)
    return '{}" rel="noopener noreferrer" target="_blank">{}'.format(url,name)
def make_clickable(url,name):
    return  (f'''<a href="{url}" rel="noopener noreferrer" target="_blank">{name}</a>''')

def GetData(market):
    data = {'1h':[], '1d':[] ,'1wk':[] , '5m':[],'15m':[],'30m':[],'60m':[],'90m':[],'4h':[]}
    for tf in data:
        rel_path = 'TA-Lib Signals/{}/{}/'.format(market,tf)
        abs_dir =GLOBAL.ABSOLUTE(rel_path,local)
        if(os.path.exists(abs_dir)):
            paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
            for path in paths:
                df = pd.read_csv(path)
                data[tf].append(df)
                del df
    return data
def sq_match(c,sq):
    if(c=='Coin' or c=='Symbol'):
        t=str(c).split('>')[1].split('<')[0]
        if(t.lower().__contains__(sq.lower())):
            return 1
    else:
        if(str(c).lower().__contains__(sq.lower())):
            return 1

    return 0
def tables(data,exchange='Kucoin',sq='sma entry'):
    # streaml='http://localhost:8501/'
    streaml='http://trader.baharsoft.com:8100/'
    tables = {'5m': [],
                '15m': [],
                '30m': [],
                '60m': [],
                '90m': [],
                '1h': [],
                '4h': [],
                '1d': [],
                '1wk': []}
    for d in data:
        if(data[d]):
            df=data[d][-1]
            sym='Coin'
            if 'Symbol' in df.columns: sym='Symbol'
            pretty = df[[
                    f'{sym}', 'date time','volume']].sort_values(by=['volume'], ascending=False)
            if('entry' in df.columns):
                pretty = df[[
                        f'{sym}', 'date time','entry']].sort_values(by=['entry'], ascending=False)
            if('bullish patterns' in df.columns):
                pretty ['bullish patterns']=df[['bullish patterns']]
                pretty ['bullish']=df[['bullish']]
            if('bearish patterns' in df.columns):
                pretty ['bearish patterns']=df[['bearish patterns']]
                pretty ['bearish']=df[['bearish']]
            if('breaking out' in df.columns):
                pretty ['breaking out']=df[['breaking out']]
            if('bollinger' in df.columns):
                pretty ['bollinger']=df[['bollinger']]
            if('rsi' in df.columns):
                pretty ['rsi']=df[['rsi']]
            if('ema' in df.columns):
                pretty ['ema']=df[['ema']]
            if('sma' in df.columns):
                pretty ['sma']=df[['sma']]
            if('force' in df.columns):
                pretty ['force']=df[['force']]
            if('ML' in df.columns):
                pretty ['ML']=df[['ML']]
            if('double_bot' in df.columns):
                pretty ['double_bot']=df[['double_bot']]

            pretty['url']=pretty[f'{sym}'].apply(makelink,streaml=streaml,exch=exchange,tf=d)
            pretty[f'{sym}'] = pretty.apply(lambda x: make_clickable(x['url'],x[f'{sym}']), axis=1)
            # pretty.style
            pretty.__delitem__('url')
            if(sq!=''): 
                all=[]
                for c in pretty.columns:
                    pretty['sq']=pretty[c].apply(sq_match,sq=sq)
                    filtered=pretty[pretty['sq']==1]
                    if(len(filtered)>0):
                        all.append(filtered)

                if len(all)>0:
                    pretty=pd.concat(all).drop_duplicates().sort_index()
                else:
                    pretty.drop(pretty.index, inplace=True)

                pretty.__delitem__('sq')
                del all
                gc.collect()
            tables[d].append(pretty)
            del df
            gc.collect()
    del data
    gc.collect()
    return tables

def crypto_signals():
    data = GetData(market='Kucoin')
    if (len(data) > 0):
        sq=st.text_input(label='',placeholder='Serch Coin or method ...')
        all_tables=tables(data,exchange='Kucoin',sq=sq)
        for table in all_tables:
            if(len(all_tables[table])>0):
                st.subheader(f'Time Frame: {table}')

                st.write(all_tables[table][0].to_html(escape=False, index=False), unsafe_allow_html=True)
                st.markdown("""---""")
        del all_tables
        del data
        gc.collect()
def stocks_signals():
    data = GetData(market='Yahoo')
    if (len(data) > 0):
        sq=st.text_input(label='',placeholder='Serch Symbol or method ...')
        all_tables=tables(data,exchange='Yahoo',sq=sq)
        for table in all_tables:
            if(len(all_tables[table])>0):
                st.subheader(f'Time Frame: {table}')

                st.write(all_tables[table][0].to_html(escape=False, index=False), unsafe_allow_html=True)
                st.markdown("""---""")
with st.sidebar:
    market=st.selectbox('Market',['Crypto','US Stock','Forex'])

if market=='Crypto':
    crypto_signals()
if market=='US Stock':
    stocks_signals()