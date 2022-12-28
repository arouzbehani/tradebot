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
    data = {'1h':[], '1d':[] , '30m':[],'4h':[]}
    for tf in data:
        rel_path = 'TA-Lib Signals/{}/{}/'.format(market,tf)
        abs_dir = os.path.join(BASE_DIR, rel_path)
        if(relp):
            abs_dir=rel_path
        paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
        for path in paths:
            df = pd.read_csv(path)
            data[tf].append(df)
    return data


def makelink(c,streaml,exch,tf):
    return '{}?symbol={}&exch={}&tf={}'.format(streaml,c.replace('/','_'),exch,tf)
def make_clickablez(name,streaml,exch,tf):
    url='{}?symbol={}&exch={}&tf={}'.format(streaml,name.replace('/','_'),exch,tf)
    return '{}" rel="noopener noreferrer" target="_blank">{}'.format(url,name)
def make_clickable(url,name):
    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url,name)
@app.route("/talib")
def talib():
    return redirect(url_for('signals'))

@app.route("/signals")  # this sets the route to this page
def signals():
    # streaml='http://localhost:8501/'
    streaml='http://trader.baharsoft.com:8100/'

    data = GetData(market='Kucoin',relp=False)
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        tables = {'30m': [],
                    '1h': [],
                    '4h': [],
                    '1d': []}
        for d in data:
            if(data[d]):
                df=data[d][-1]
                pretty = df[[
                        'Coin', 'date time','volume']].sort_values(by=['volume'], ascending=False)
                if('entry' in df.columns):
                    pretty = df[[
                            'Coin', 'date time','entry']].sort_values(by=['entry'], ascending=False)

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

                pretty['url']=pretty['Coin'].apply(makelink,streaml=streaml,exch='Kucoin',tf=d)
                pretty['Coin'] = pretty.apply(lambda x: make_clickable(x['url'],x['Coin']), axis=1)
                pretty.style
                pretty.__delitem__('url')


                html=pretty.to_html(classes='table table-striped',table_id="pretty_table_{}".format(d),escape=False,render_links=True)
                tables[d].append(HTML(html))

        return render_template('signals.html', tables=tables)
    else:
        return render_template('signals.html', "", "")


if __name__ == "__main__":
    app.run()
