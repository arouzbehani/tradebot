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


def GetData():
    BASE_DIR = '/root/trader_webapp'
    data = {'1h':[], '1d':[]}
    for tf in data:
        rel_path = 'TA-Lib Signals/'+tf+'/'
        abs_dir = os.path.join(BASE_DIR, rel_path)
        #abs_dir=rel_path
        print(abs_dir)
        paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
        print(paths)
        # for path in os.listdir(abs_dir):
        for path in paths:
            # check if current path is a file
            # if os.path.isfile(os.path.join(abs_dir, path)):
                #df = pd.read_csv(os.path.join(abs_dir, path))
            df = pd.read_csv(path)
            data[tf].append(df)
                # print(df)
    return data


@app.route("/talib")  # this sets the route to this page
def talib():
    data = GetData()
    print(str(len(data)))
    # data[0]['Trading View']=data[0]['Coin'].map(tourl)
    if (len(data) > 0):
        tables = {'1h_bullish': [],
                  '1h_bearish': [],
                  '1d_bullish': [],
                  '1d_bearish': []}
        for d in data:
            pretty_bullish = data[d][len(data[d])-1][[
                'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
            pretty_bearish = data[d][len(data[d])-1][[
                'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
            tables[d+'_bullish'].append(HTML(pretty_bullish.to_html(classes='table table-hovered')))
            tables[d+'_bearish'].append(HTML(pretty_bearish.to_html(classes='table table-hovered')))

        return render_template('talib.html', tables=tables)
    else:
        return render_template('talib.html', "", "")





if __name__ == "__main__":
    app.run()
