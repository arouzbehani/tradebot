import argparse
import helper
import talib
import pandas as pd
import patterns

def find(symbol='BTC_USDT',tf='1h',exchange='Kucoin',n=50):
    df=helper.GetData(tf=tf,exch=exchange,symbol=symbol)
    df=df[-100:].reset_index(drop=True)
    df["time"] = pd.to_datetime(df["timestamp"], unit="ms")

    bullish_reversal_patterns = [
        "CDLDOJI",
        "CDLENGULFING",
        "CDLHAMMER",
        "CDLINVERTEDHAMMER",
        "CDLHARAMI",
        "CDLMORNINGSTAR",
        "CDL3WHITESOLDIERS",
    ]
    bearish_reversal_patterns = [
        "CDLDOJI",
        "CDLENGULFING",
        "CDLHANGINGMAN",
        "CDLSHOOTINGSTAR",
        "CDLHARAMI",
        "CDLEVENINGSTAR",
        "CDL3BLACKCROWS",
    ]
    patts=[bullish_reversal_patterns,bearish_reversal_patterns]        
    #matching = []
    for pat in patts:
        if pat==bullish_reversal_patterns:print("BULLISH Patterns")
        if pat==bearish_reversal_patterns:print("BEARISH Patterns")
        for index,candle in df.iterrows():
            if index>n:
                for p in pat:
                    func = getattr(talib, p)
                    last_n_rows = df[-len(df)+index-n:-len(df)+index]
                    res = (
                        func(
                            last_n_rows["open"],
                            last_n_rows["high"],
                            last_n_rows["low"],
                            last_n_rows["close"],
                        )
                    ).reset_index()
                    if pat==bullish_reversal_patterns:
                        if res[-1:][0].values[0] > 0:
                            p_time=last_n_rows.iloc[-1].time
                            print(f'{patterns.patterns[p]} -- {p_time}')
                            #matching.append(f'{patterns.patterns[p]} -- {p_time}')
                    else:
                        if res[-1:][0].values[0] < 0:
                            p_time=last_n_rows.iloc[-1].time
                            print(f'{patterns.patterns[p]} -- {p_time}')
                            #matching.append(f'{patterns.patterns[p]} -- {p_time}')                
    #print(matching)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("argument", nargs="+", type=str, help="Your desired argument (optional)")
    args = parser.parse_args()
    if not args.argument is None:
        find(tf=args.argument[0],symbol=args.argument[1])
    else:
        find()