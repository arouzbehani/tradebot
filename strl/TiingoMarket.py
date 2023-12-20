import calendar
from datetime import datetime
from datetime import timedelta
import gc
import os
import GLOBAL
import requests
import pandas as pd
import config


def to_utc(t):
    return int(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() * 1000)


def GetMarkets(local=False):
    rel_path = "Market Data/Forex/tickers.csv"
    df = pd.read_csv(GLOBAL.ABSOLUTE(rel_path, local))
    return list(df["Ticker"])


secret = ""


def GetMarketData(markets, period=60, tf="1day", ticker="All", local=False,secret=''):
    marketData = []
    errordata = []
    now = datetime.utcnow()  # + timedelta(hours=-5)
    before = now + timedelta(days=-1 * period)
    if ticker != "All":
        simple = [t for t in markets if t == ticker]
        markets = simple
    for m in markets:
        try:
            headers = {"Content-Type": "application/json"}

            ticker = m.replace("/", "")
            print(f"Downloading Ticker:{ticker} -- tf:{tf}")
            # 2020-01-01
            # 2021-02-19
            # 2022-03-11
            # 2023-05-01
            startdate=f'{before.year}-{before.month}-{before.day}'
            base_url = "https://api.tiingo.com/tiingo/fx/{}/prices?startDate={}&resampleFreq={}&token={}".format(
                ticker,startdate, tf, secret
            )
            requestResponse = requests.get(base_url, headers=headers)
            data = requestResponse.json()
            df_tiingo = pd.DataFrame.from_dict(data).reset_index()
            df_tiingo["timestamp"] = df_tiingo["date"].apply(to_utc)
            df_tiingo["volume"] = 1

            df = pd.DataFrame(
                df_tiingo,
                columns=["timestamp", "open", "high", "low", "close", "volume"],
            )
            df["Ticker"] = m
            rel_path = "Market Data/Forex/{}/{}__{}.csv".format(
                tf, m.replace("/", "_"), tf
            )
            abs_path = GLOBAL.ABSOLUTE(rel_path, local)
            if os.path.isfile(abs_path):
                df0 = pd.read_csv(abs_path)
                fdf = (
                    pd.concat([df, df0])
                    .drop_duplicates(subset=["timestamp"])
                    .sort_values(by=["timestamp"])
                )
                fdf.to_csv(abs_path, header=True, index=False, sep=",", mode="w")

            else:
                fdf = df
                fdf.to_csv(abs_path, header=True, index=False, sep=",", mode="w")

            marketData.append(df)
            del df_tiingo
            del df
            del df0
            del fdf
            gc.collect()
        except:
            print("error in fetching market data for: " + m + " --- tf:" + tf)
            errordata.append(m + ":" + tf)
    return (marketData, errordata)
