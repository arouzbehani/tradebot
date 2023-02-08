import streamlit as st
import os , gc , GLOBAL
import pandas  as pd
from pathlib import Path
from streamlit.components.v1 import html
local =True

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
def tables(data,exchange='Kucoin'):
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
                print('double bot')
                pretty ['double_bot']=df[['double_bot']]
            else:
                print('no double bot')

            pretty['url']=pretty[f'{sym}'].apply(makelink,streaml=streaml,exch=exchange,tf=d)
            pretty[f'{sym}'] = pretty.apply(lambda x: make_clickable(x['url'],x[f'{sym}']), axis=1)
            # pretty.style
            pretty.__delitem__('url')


            html=pretty.to_html(classes='table table-striped',table_id="pretty_table_{}".format(d),escape=False,render_links=True)
            # tables[d].append(HTML(html))
            tables[d].append(pretty)
            del df
    del data
    gc.collect()
    return tables

def crypto_signals():

    data = GetData(market='Kucoin')
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        all_tables=tables(data,exchange='Kucoin')
        for table in all_tables:
            if(len(all_tables[table])>0):
                st.write(all_tables[table][0].to_html(escape=False, index=False), unsafe_allow_html=True)

def stocks_signals():

    data = GetData(market='Yahoo')
    all_tables=tables(data,exchange='Yahoo')
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        for table in all_tables:
            st.write(table.to_html(escape=False, index=False), unsafe_allow_html=True)



crypto_signals()

my_js="""
    $(document).on('keyup', 'input', function () {
      var id=$(this)[0].id;
                tf=id.split('_')[2]
                tableid=id.split('_')[0]+"_table_"+tf
                var value = $(this).val();
                $("table#"+tableid+" tr").each(function (index) {
                    if (index != 0) {

                        $row = $(this);

                        var coin = $row.find("td:first").text();
                        var pattern = $row.find("td:nth-child(5)").text();
                        // var brout = $row.find("td:nth-child(5)").text();
                        var bb = $row.find("td:nth-child(6)").text();
                        var rsi = $row.find("td:nth-child(7)").text();
                        // var ema = $row.find("td:nth-child(8)").text();
                        var sma = $row.find("td:nth-child(8)").text();
                        // var force = $row.find("td:nth-child(10)").text();
                        var db_b = $row.find("td:nth-child(9)").text();
                        
                        if (!(
                            coin.toLowerCase().includes(value.toLowerCase()) || 
                            pattern.toLowerCase().includes(value.toLowerCase()) || 
                            // brout.toLowerCase().includes(value.toLowerCase()) ||
                            bb.toLowerCase().includes(value.toLowerCase()) ||
                            rsi.toLowerCase().includes(value.toLowerCase()) ||
                            // ema.toLowerCase().includes(value.toLowerCase()) ||
                            sma.toLowerCase().includes(value.toLowerCase()) ||
                            // force.toLowerCase().includes(value.toLowerCase()) ||
                            db_b.toLowerCase().includes(value.toLowerCase()) 

                            )
                            
                            ) {
                            $(this).hide();
                        }
                        else {
                            $(this).show();
                        }
                    }
                });
})

"""
my_html = f"<script>{my_js}</script>"
html(my_html)

