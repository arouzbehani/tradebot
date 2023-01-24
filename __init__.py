import os
from flask import Flask, jsonify, render_template,redirect,url_for
import pandas as pd
from pathlib import Path
from IPython.display import HTML
app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey123"
app.debug = True

def tourl(c):
    return "https://www.tradingview.com/chart?symbol=KUCOIN%3"+c.replace('/', '')


@app.route("/")  # this sets the route to this page
def home():
    return jsonify({'Messasge': "Testissng"})


@app.route('/about')
def about():
    return render_template('about.html', organization='About Traqqqder')


def GetData(market,relp=False):
    BASE_DIR = '/root/trader_webapp'
    data = {'1h':[], '1d':[] ,'1wk':[] , '5m':[],'15m':[],'30m':[],'60m':[],'90m':[],'4h':[]}
    for tf in data:
        rel_path = 'TA-Lib Signals/{}/{}/'.format(market,tf)
        abs_dir = os.path.join(BASE_DIR, rel_path)
        if(relp):
            abs_dir=rel_path
        if(os.path.exists(abs_dir)):
            paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
            for path in paths:
                df = pd.read_csv(path)
                data[tf].append(df)
    return data


def makelink(c,streaml,exch,tf):
    return '{}chart?symbol={}&exch={}&tf={}'.format(streaml,c.replace('/','_'),exch,tf)
def make_clickablez(name,streaml,exch,tf):
    url='{}?chartsymbol={}&exch={}&tf={}'.format(streaml,name.replace('/','_'),exch,tf)
    return '{}" rel="noopener noreferrer" target="_blank">{}'.format(url,name)
def make_clickable(url,name):
    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url,name)
@app.route("/talib")
def talib():
    return redirect(url_for('signals'))

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

            pretty['url']=pretty[f'{sym}'].apply(makelink,streaml=streaml,exch=exchange,tf=d)
            pretty[f'{sym}'] = pretty.apply(lambda x: make_clickable(x['url'],x[f'{sym}']), axis=1)
            pretty.style
            pretty.__delitem__('url')


            html=pretty.to_html(classes='table table-striped',table_id="pretty_table_{}".format(d),escape=False,render_links=True)
            tables[d].append(HTML(html))
    return tables
@app.route("/signals")
def signals():
    data = GetData(market='Kucoin',relp=False)
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        
        return render_template('signals.html', tables=tables(data,exchange='Kucoin'))
    else:
        return render_template('signals.html', "", "")

@app.route("/signals/crypto")  # this sets the route to this page
def crypto_signals():

    data = GetData(market='Kucoin',relp=False)
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        
        return render_template('signals.html', tables=tables(data,exchange='Kucoin'))
    else:
        return render_template('signals.html', "", "")

@app.route("/signals/stocks")  # this sets the route to this page
def stocks_signals():

    data = GetData(market='Yahoo',relp=False)
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        
        return render_template('signals.html', tables=tables(data,exchange='Yahoo'))
    else:
        return render_template('signals.html', "", "")


if __name__ == "__main__":
    app.run()
