import os
from flask import Flask, jsonify, render_template
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

@app.route("/signals")
def signals():
    data = GetData(market='Kucoin',relp=False)
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        tables = {'30m': [],
                    '1h': [],
                    '4h': [],
                    '1d': []}
        for d in data:
            if(data[d]):
                pretty_bullish = data[d][len(data[d])-1][[
                    'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
                pretty_bearish = data[d][len(data[d])-1][[
                    'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
                tables[d].append(HTML(pretty_bullish.to_html(classes='table table-striped')))
                tables[d].append(HTML(pretty_bearish.to_html(classes='table table-striped')))

        return render_template('talib.html', tables=tables)
    else:
        return render_template('talib.html', "", "")

def makelink(c,streaml,exch,tf):
    return '{}?symbol={}&exch={}&tf={}'.format(streaml,c.replace('/','_'),exch,tf)
def make_clickablez(name,streaml,exch,tf):
    url='{}?symbol={}&exch={}&tf={}'.format(streaml,name.replace('/','_'),exch,tf)
    return '{}" rel="noopener noreferrer" target="_blank">{}'.format(url,name)
def make_clickable(url,name):
    return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url,name)

@app.route("/talib")  # this sets the route to this page
def talib():
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
                pretty_bullish = df[[
                        'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)

                if('breaking out' in df.columns):
                    pretty_bullish ['breaking out']=df[['breaking out']]
                if('bollinger' in df.columns):
                    pretty_bullish ['bollinger']=df[['bollinger']]

                pretty_bullish['url']=pretty_bullish['Coin'].apply(makelink,streaml=streaml,exch='Kucoin',tf=d)
                pretty_bullish['Coin'] = pretty_bullish.apply(lambda x: make_clickable(x['url'],x['Coin']), axis=1)
                pretty_bullish.style
                pretty_bullish.__delitem__('url')

                pretty_bearish = df[[
                    'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
                if('breaking out' in df.columns):
                    pretty_bearish ['breaking out']=df[['breaking out']]
                if('bollinger' in df.columns):
                    pretty_bearish ['bollinger']=df[['bollinger']]

                pretty_bearish['url']=pretty_bearish['Coin'].apply(makelink,streaml=streaml,exch='Kucoin',tf=d)
                pretty_bearish['Coin'] = pretty_bearish.apply(lambda x: make_clickable(x['url'],x['Coin']), axis=1)
                pretty_bearish.style
                pretty_bearish.__delitem__('url')

                bull_htm=pretty_bullish.to_html(classes='table table-striped',table_id="bullish_table_{}".format(d),escape=False,render_links=True)
                bear_htm=pretty_bearish.to_html(classes='table table-striped',table_id="bearish_table_{}".format(d),escape=False,render_links=True)
                tables[d].append(HTML(bull_htm))
                tables[d].append(HTML(bear_htm))

        return render_template('talib.html', tables=tables)
    else:
        return render_template('talib.html', "", "")





if __name__ == "__main__":
    app.run()
