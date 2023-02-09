import GLOBAL
from pathlib import Path
import pandas as pd
import numpy as np
from ta.volatility import BollingerBands as bb
from ta.momentum import RSIIndicator as rsi
from ta.trend import ADXIndicator as adx
from ta.trend import EMAIndicator as ema
from ta.trend import SMAIndicator as sma
from ta.trend import MACD as macd
from ta.trend import IchimokuIndicator as ichi
from ta.volume import ForceIndexIndicator as fi


local = False


def GetData(tf, symbol, exch):
    df = None
    rel_dir = 'Market Data/{}/{}/'.format(exch, tf, symbol)
    # rel_dir='Market Data/{}/{}/'.format(exch,tf,symbol)
    abs_dir = GLOBAL.ABSOLUTE(rel_dir, local)
    for path in Path(abs_dir).iterdir():
        if (path.name.lower().startswith(symbol.lower())):
            df = pd.read_csv(path)

            break
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')

    return df


def GetAllData(exch='Kucoin'):
    tfs = ['30m', '1h', '4h', '1d']
    markets = []
    for tf in tfs:
        rel_dir = 'Market Data/{}/{}'.format(exch, tf)
        abs_dir = GLOBAL.ABSOLUTE(rel_dir, local)
        for path in Path(abs_dir).iterdir():
            try:
                df = pd.read_csv(path)
                markets.append({path.name: df})
            except:
                print(f'error in reading {path}')

    return markets


def is_consolidating(closes, percentage=2):
    max_close = closes.max()
    min_close = closes.min()
    threshold = 1-(percentage/100)
    if min_close > (max_close * threshold):
        return True
    return False


def brout_check(df, candles=15):
    for index in df.index:
        if (index >= candles):
            last_close = df['close'][index]
            if (is_consolidating(df['close'][index-candles-1:index-1], percentage=10)):
                if (last_close > df['close'][index-candles-1:index-1].max()):
                    df['brout'][index] = 1
                else:
                    df['brout'][index] = np.nan
            else:
                df['brout'][index] = np.nan
        else:
            df['brout'][index] = np.nan

    return df


def append_adx(df):
    adx_indicator = adx(
        high=df['high'], low=df['low'], close=df['close'], window=14, fillna=False)
    df['adx'] = adx_indicator.adx()
    df['adx_neg'] = adx_indicator.adx_neg()
    df['adx_pos'] = adx_indicator.adx_pos()
    df['adx_pos_neg'] = adx_indicator.adx_pos()/adx_indicator.adx_neg()
    df['adx_signal_marker'] = np.where(np.logical_and(np.logical_and(
        df['adx'] > 25, df['adx_pos'] > df['adx_neg']), df['adx'].shift(1) < 25), df['close'], np.nan)
    df['adx_signal'] = np.where(np.logical_and(
        df['adx'] > 25, df['adx_pos'] > df['adx_neg']), df['close'], np.nan)
    return df


def append_ichi(df):
    ich_indicator = ichi(
        high=df['high'], low=df['low'], window1=9, window2=26, window3=52, visual=True, fillna=False)
    df['ich_a'] = ich_indicator.ichimoku_a()
    df['ich_b'] = ich_indicator.ichimoku_b()
    df['ich_base_line'] = ich_indicator.ichimoku_base_line()
    df['ich_conversion_line'] = ich_indicator.ichimoku_conversion_line()
    df['ich_komo_color'] = df['ich_a'] - df['ich_b']
    return df


def append_fi(df):
    fi_indicator = fi(close=df['close'],
                      volume=df['volume'], window=15, fillna=False)
    df['fi'] = fi_indicator.force_index()
    abs_mean = (df['fi'].max()+abs(df['fi'].min()))/2
    df['fi_norm'] = df['fi']/abs_mean
    df['fi_entry_signal'] = np.where(np.logical_and(
        df['fi_norm'] >= 0.15,  df['fi_norm'].shift(1) < 0.15), df['close'], np.nan)
    return df


def append_bb(df, entry_signal=False, entry_signal_mode='Uptrend'):
    indicator_bb = bb(close=df['close'], window=20,
                      window_dev=2, fillna=False)
    df['upperband'] = indicator_bb.bollinger_hband()
    df['middleband'] = indicator_bb.bollinger_mavg()
    df['lowerband'] = indicator_bb.bollinger_lband()
    df['pband'] = indicator_bb.bollinger_pband()
    if (entry_signal):
        if (entry_signal_mode == 'Uptrend'):

            df['bb_entry_signal'] = np.where(np.logical_and(df['adx_signal'].isnull() == False,
                                                            np.logical_and(df['close'] > df['lowerband'],
                                                                           np.logical_and(df['pband'].shift(1) <= 0.05, df['close'].shift(1) < df['lowerband'].shift(1)))), df['close'], np.nan)
            df['bb_sq_entry_signal'] = np.where(np.logical_and(df['adx_signal'].isnull() == False,
                                                               np.logical_and(df['close'] > df['upperband'], np.logical_and(
                                                                   df['pband'].shift(1) >= 1, df['close'].shift(1) > df['upperband'].shift(1)))), df['close'], np.nan)
        else:
            df['bb_entry_signal'] = np.where(np.logical_and(df['close'] > df['lowerband'],
                                                            np.logical_and(df['pband'].shift(1) <= 0.05,  df['close'].shift(1) < df['lowerband'].shift(1))), df['close'], np.nan)

            df['bb_sq_entry_signal'] = np.where(np.logical_and(df['close'] > df['upperband'], np.logical_and(
                df['pband'].shift(1) >= 1, df['close'].shift(1) > df['upperband'].shift(1))), df['close'], np.nan)

    return df


def append_rsi(df, entry_signal=False, entry_signal_mode='Uptrend'):
    rsi_indicator = rsi(close=df['close'], window=14, fillna=False)
    df['rsi'] = rsi_indicator.rsi()
    if (entry_signal):
        if (entry_signal_mode == 'Uptrend'):
            df['rsi_entry_signal'] = np.where(np.logical_and(df['adx_signal'].isnull() == False,
                                                             np.logical_and(df['rsi'] < 30, df['rsi'].shift(1) > 30)), df['close'], np.nan)
        else:
            df['rsi_entry_signal'] = np.where(np.logical_and(
                df['rsi'] < 30, df['rsi'].shift(1) > 30), df['close'], np.nan)


def append_sma(df, entry_signal=False, entry_signal_mode='Uptrend'):
    sma_indicator_5 = sma(
        close=df['close'], window=5, fillna=False)
    sma_indicator_10 = sma(
        close=df['close'], window=10, fillna=False)
    sma_indicator_30 = sma(
        close=df['close'], window=30, fillna=False)
    df['sma_5'] = sma_indicator_5.sma_indicator()
    df['sma_10'] = sma_indicator_10.sma_indicator()
    df['sma_30'] = sma_indicator_30.sma_indicator()
    if (entry_signal):
        if (entry_signal_mode == 'Uptrend'):
            df['sma_entry_signal'] = np.where(np.logical_and(df['adx_signal'].isnull() == False,
                                                             np.logical_and(np.logical_and(np.logical_and(df['sma_30'] / df['sma_10'] >= 0.99, df['sma_30'] / df['sma_10'] <= 1), df['sma_10'] < df['sma_5']),
                                                                            np.logical_or(np.logical_or(df['sma_30'].shift(1) > df['sma_10'].shift(1), df['sma_10'].shift(1) > df['sma_5'].shift(1)), df['sma_30'].shift(1) > df['sma_5'].shift(1)))), df['sma_30'], np.nan)
        else:
            df['sma_entry_signal'] = np.where(np.logical_and(np.logical_and(np.logical_and(df['sma_30'] / df['sma_10'] >= 0.99, df['sma_30'] / df['sma_10'] <= 1), df['sma_10'] < df['sma_5']),
                                                             np.logical_or(np.logical_or(df['sma_30'].shift(1) > df['sma_10'].shift(1), df['sma_10'].shift(1) > df['sma_5'].shift(1)), df['sma_30'].shift(1) > df['sma_5'].shift(1))), df['sma_30'], np.nan)

    df['sma_exit_signal'] = np.where(np.logical_and(
        df['sma_30'] > df['sma_10'], df['sma_10'] > df['sma_5']), df['close'], np.nan)


def append_sma_2(df, entry_signal=False, w1=10, w2=50):
    sma_indicator_1 = sma(
        close=df['close'], window=w1, fillna=False)
    sma_indicator_2 = sma(
        close=df['close'], window=w2, fillna=False)
    df['sma_1'] = sma_indicator_1.sma_indicator()
    df['sma_2'] = sma_indicator_2.sma_indicator()
    if (entry_signal):
        cf=1.001 ## coefficient for approving postive or negative change 
        df['sma_entry_signal'] = np.where(
                                            np.logical_or
                                            (
                                                np.logical_and  ### sma 2 is below sma 1 but just positive move for sma 2 has occured
                                                (
                                                    np.logical_and(df['sma_2'] < df['sma_1'],df['sma_2'].shift(1)<df['sma_1'].shift(1))
                                                    ,
                                                    np.logical_and(df['sma_2'] > df['sma_2'].shift(1)*cf,df['sma_2'].shift(1)<df['sma_2'].shift(2))
                                                )
                                                ,
                                                np.logical_and
                                                (
                                                    np.logical_and
                                                    (
                                                        np.logical_and
                                                        (
                                                            df['sma_1']>df['sma_1'].shift(1) ### Controling Positive Slope with this candle and a candle behind
                                                            ,
                                                            df['sma_2']>df['sma_2'].shift(1)*cf
                                                        )
                                                        ,
                                                        np.logical_and
                                                        (
                                                            df['sma_2'] / df['sma_1']>=0.99   ### 1 percent tolerance for satidfying "Entry Signal" condition
                                                            ,
                                                            df['sma_2'] / df['sma_1']<=1
                                                        )
                                                    
                                                    )
                                                    ,
                                                    (
                                                        df['sma_2'].shift(1) > df['sma_1'].shift(1) ### A Candle Just Before "Entry Signal" Area
                                                    )  
                                                )
                                            )
                                          , 
                                          df['sma_2'], np.nan
                                        )
        df['sma_exit_signal'] = np.where(
                                            np.logical_or
                                            (
                                                np.logical_and  ### sma 2 is above sma 1 but just negative move for sma 2 has occured
                                                (
                                                    np.logical_and(df['sma_1'] < df['sma_2'],df['sma_1'].shift(1)<df['sma_2'].shift(1))
                                                    ,
                                                    np.logical_and(df['sma_2'] < df['sma_2'].shift(1)*cf,df['sma_2'].shift(1)>df['sma_2'].shift(2))
                                                )
                                                ,
                                                np.logical_and
                                                (
                                                    np.logical_and
                                                    (
                                                        np.logical_and
                                                        (
                                                            df['sma_1']<df['sma_1'].shift(1) ### Controling Negative Slope with this candle and a candle behind
                                                            ,
                                                            df['sma_2']<df['sma_2'].shift(1)
                                                        )
                                                        ,
                                                        np.logical_and
                                                        (
                                                            df['sma_1'] / df['sma_2']>=0.99   ### 1 percent tolerance for satidfying "Exit Signal" condition
                                                            ,
                                                            df['sma_1'] / df['sma_2']<=1
                                                        )
                                                    
                                                    )
                                                    ,
                                                    (
                                                        df['sma_1'].shift(1) > df['sma_2'].shift(1) ### A Candle Just Before "Exit Signal" Area
                                                    )  
                                                )
                                            )
                                          , 
                                          df['sma_1'], np.nan
                                        )                                        

def append_ema(df, entry_signal=False, entry_signal_mode='Uptrend'):
    ema_indicator_5 = ema(
        close=df['close'], window=5, fillna=False)
    ema_indicator_10 = ema(
        close=df['close'], window=10, fillna=False)
    ema_indicator_30 = ema(
        close=df['close'], window=30, fillna=False)
    df['ema_5'] = ema_indicator_5.ema_indicator()
    df['ema_10'] = ema_indicator_10.ema_indicator()
    df['ema_30'] = ema_indicator_30.ema_indicator()
    if (entry_signal):
        if (entry_signal_mode == 'Uptrend'):
            df['ema_entry_signal'] = np.where(np.logical_and(df['adx_signal'].isnull() == False,
                                                             np.logical_and(np.logical_and(df['ema_30'] < df['ema_10'], df['ema_10'] < df['ema_5']),
                                                                            np.logical_or(np.logical_or(df['ema_30'].shift(1) > df['ema_10'].shift(1), df['ema_10'].shift(1) > df['ema_5'].shift(1)), df['ema_30'].shift(1) > df['ema_5'].shift(1)))), df['ema_30'], np.nan)
        else:
            df['ema_entry_signal'] = np.where(np.logical_and(np.logical_and(df['ema_30'] < df['ema_10'], df['ema_10'] < df['ema_5']),
                                                             np.logical_or(np.logical_or(df['ema_30'].shift(1) > df['ema_10'].shift(1), df['ema_10'].shift(1) > df['ema_5'].shift(1)), df['ema_30'].shift(1) > df['ema_5'].shift(1))), df['ema_30'], np.nan)


def append_macd(df):
    macd_indicator = macd(
        close=df['close'], window_slow=26, window_fast=12, window_sign=9, fillna=False)
    df['macd'] = macd_indicator.macd()
    df['macd_diff'] = macd_indicator.macd_diff()
    df['macd_signal'] = macd_indicator.macd_signal()
