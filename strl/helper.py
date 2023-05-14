import itertools
from sklearn.metrics import r2_score
import GLOBAL
import gc
import Constants as c
from pathlib import Path
import pandas as pd
import numpy as np
from ta.volatility import BollingerBands as bb
from ta.momentum import RSIIndicator as rsi
from ta.momentum import StochasticOscillator as oscill
from ta.trend import ADXIndicator as adx
from ta.trend import EMAIndicator as ema
from ta.trend import SMAIndicator as sma
from ta.trend import MACD as macd
from ta.trend import IchimokuIndicator as ichi
from ta.volume import ForceIndexIndicator as fi
from statistics import mean
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True

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
    df['ich_moku_color'] = df['ich_a'] - df['ich_b']

    return df


def append_stochastic(df):
    oscill_indicator = oscill(
        high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3, fillna=False)
    df['oscill_signal'] = oscill_indicator.stoch_signal
    df['oscill_stoch'] = oscill_indicator.stoch

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
        cf = 1.001  # coefficient for approving postive or negative change
        df['sma_entry_signal'] = np.where(
            np.logical_or
            (
                np.logical_and  # sma 2 is below sma 1 but just positive move for sma 2 has occured
                (
                    np.logical_and(df['sma_2'] < df['sma_1'], df['sma_2'].shift(
                        1) < df['sma_1'].shift(1)),
                    np.logical_and(df['sma_2'] > df['sma_2'].shift(
                        1)*cf, df['sma_2'].shift(1) < df['sma_2'].shift(2))
                ),
                np.logical_and
                (
                    np.logical_and
                    (
                        np.logical_and
                        (
                            # Controling Positive Slope with this candle and a candle behind
                            df['sma_1'] > df['sma_1'].shift(1),
                            df['sma_2'] > df['sma_2'].shift(
                                1)*cf
                        ),
                        np.logical_and
                        (
                            # 1 percent tolerance for satidfying "Entry Signal" condition
                            df['sma_2'] / df['sma_1'] >= 0.99,
                            df['sma_2'] / \
                            df['sma_1'] <= 1
                        )

                    ),
                    (
                        # A Candle Just Before "Entry Signal" Area
                        df['sma_2'].shift(
                            1) > df['sma_1'].shift(1)
                    )
                )
            ),
            df['sma_2'], np.nan
        )
        df['sma_exit_signal'] = np.where(
            np.logical_or
            (
                np.logical_and  # sma 2 is above sma 1 but just negative move for sma 2 has occured
                (
                    np.logical_and(df['sma_1'] < df['sma_2'], df['sma_1'].shift(
                        1) < df['sma_2'].shift(1)),
                    np.logical_and(df['sma_2'] < df['sma_2'].shift(
                        1)*cf, df['sma_2'].shift(1) > df['sma_2'].shift(2))
                ),
                np.logical_and
                (
                    np.logical_and
                    (
                        np.logical_and
                        (
                            # Controling Negative Slope with this candle and a candle behind
                            df['sma_1'] < df['sma_1'].shift(1),
                            df['sma_2'] < df['sma_2'].shift(
                                1)
                        ),
                        np.logical_and
                        (
                            # 1 percent tolerance for satidfying "Exit Signal" condition
                            df['sma_1'] / df['sma_2'] >= 0.99,
                            df['sma_1'] / \
                            df['sma_2'] <= 1
                        )

                    ),
                    (
                        # A Candle Just Before "Exit Signal" Area
                        df['sma_1'].shift(
                            1) > df['sma_2'].shift(1)
                    )
                )
            ),
            df['sma_1'], np.nan
        )
    # df.to_csv('test.csv', header=True, index=True, sep=',', mode='w')


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


def Rsi_Divergence(df):
    x = np.where(df['pivot'] == 2, df['timestamp'], np.nan)
    xs_up = x[~np.isnan(x)]
    y = np.where(df['pivot'] == 2, df['pointpos'], np.nan)
    ys_up = y[~np.isnan(y)]
    last_up = ys_up[-1:][0]
    last_xs_up = xs_up[-1:][0]
    one_to_last_up = ys_up[-2:-1][0]
    one_to_last_xs_up = xs_up[-2:-1][0]
    r = np.where(df['timestamp'] == last_xs_up, df['rsi'], np.nan)
    last_rsi_up = r[~np.isnan(r)][-1:][0]
    r = np.where(df['timestamp'] == one_to_last_xs_up, df['rsi'], np.nan)
    one_to_last_rsi_up = r[~np.isnan(r)][-1:][0]

    x = np.where(df['pivot'] == 1, df['timestamp'], np.nan)
    xs_down = x[~np.isnan(x)]
    y = np.where(df['pivot'] == 1, df['pointpos'], np.nan)
    ys_down = y[~np.isnan(y)]
    last_down = ys_down[-1:][0]
    last_xs_down = xs_down[-1:][0]
    r = np.where(df['timestamp'] == last_xs_down, df['rsi'], np.nan)
    last_rsi_down = r[~np.isnan(r)][-1:][0]
    one_to_last_down = ys_down[-2:-1][0]
    one_to_last_xs_down = xs_down[-2:-1][0]
    r = np.where(df['timestamp'] == one_to_last_xs_down, df['rsi'], np.nan)
    one_to_last_rsi_down = r[~np.isnan(r)][-1:][0]

    if (last_up < one_to_last_up and last_rsi_up > one_to_last_rsi_up) or (last_up > one_to_last_up and last_rsi_up < one_to_last_rsi_up):
        return True, [pd.to_datetime(one_to_last_xs_up, unit="ms"), pd.to_datetime(last_xs_up, unit="ms")], [one_to_last_up, last_up], [pd.to_datetime(one_to_last_xs_up, unit="ms"), pd.to_datetime(last_xs_up, unit="ms")], [one_to_last_rsi_up, last_rsi_up]
    if (last_down < one_to_last_down and last_rsi_down > one_to_last_rsi_down) or (last_down > one_to_last_down and last_rsi_down < one_to_last_rsi_down):
        return True, [pd.to_datetime(one_to_last_xs_down, unit="ms"), pd.to_datetime(last_xs_down, unit="ms")], [one_to_last_down, last_down], [pd.to_datetime(one_to_last_xs_down, unit="ms"), pd.to_datetime(last_xs_down, unit="ms")], [one_to_last_rsi_down, last_rsi_down]

    return False, None, None, None, None


def ReturnTrend(xs, ys):
    coeff = np.polyfit(x=xs, y=ys, deg=1)

    yn = np.poly1d(coeff)
    r2 = r2_score(ys, yn(xs))
    return round(r2, 4), yn(xs)


def TrendDirection(df):
    pointpos_df = pd.DataFrame(
        data=df[~pd.isnull(df['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
    trend = c.Trend.Nothing
    down_xs = (pointpos_df[pointpos_df['pivot'] == 1]
               ['timestamp']).reset_index(drop=True)
    down_ys = (pointpos_df[pointpos_df['pivot'] == 1]
               ['pointpos']).reset_index(drop=True)
    _, trend_down_ys = ReturnTrend(down_xs, down_ys)

    up_xs = (pointpos_df[pointpos_df['pivot'] == 2]
             ['timestamp']).reset_index(drop=True)
    up_ys = (pointpos_df[pointpos_df['pivot'] == 2]
             ['pointpos']).reset_index(drop=True)
    _, trend_up_ys = ReturnTrend(up_xs, up_ys)
    if trend_up_ys[-1] > trend_up_ys[0] and trend_down_ys[-1] > trend_down_ys[0]:
        trend = c.Trend.Bullish
    elif trend_up_ys[-1] < trend_up_ys[0] and trend_down_ys[-1] < trend_down_ys[0]:
        trend = c.Trend.Bearish
    elif trend_up_ys[-1] > trend_up_ys[0] and trend_down_ys[-1] < trend_down_ys[0]:
        trend = c.Trend.Widening_Side
    elif trend_up_ys[-1] < trend_up_ys[0] and trend_down_ys[-1] > trend_down_ys[0]:
        trend = c.Trend.Narrowing_Side
    del pointpos_df
    del df
    # del down_xs
    # del down_ys
    # del up_xs
    # del up_ys
    # del trend_up_ys
    # del trend_down_ys
    gc.collect()
    return trend,((down_xs[0],trend_down_ys[0]),(list(down_xs)[-1],trend_down_ys[-1]) ),((up_xs[0],trend_up_ys[0]) ,(list(up_xs)[-1], trend_up_ys[-1]))

def threshold(tf,thb=1,avg_price=1):
    return thb
    tfs={'1w':10,'1d':5,'4h':2.0,'90m':1.2,'1h':1.0,'60m':1.0,'15m':0.5,'5m':0.2,'1m':0.1}

    return tfs[tf]*thb/100*avg_price

def PA_Break(df, trend_0, trend_1):
    pointpos_df = pd.DataFrame(data=df[~pd.isnull(df['pointpos'])], columns=[
                               'pivot', 'low', 'high'])
    pa_stat = c.PA_Break.Nothing
    isbreak = False
    break_level=0

    if trend_0 == c.Trend.Bearish and trend_1 == c.Trend.Bullish:
        min_low = pointpos_df['low'].values.min()
        high_before_minlow = np.where(np.logical_and(
            pointpos_df['pivot'] == 1, pointpos_df['low'] == min_low), pointpos_df.shift(1)['high'], -1).max()
        break_level=high_before_minlow
        if df[-1:]['close'].values[0] > high_before_minlow:
            pa_stat = c.PA_Break.Bearish_Break_Up
            isbreak = True
    elif trend_0 == c.Trend.Bullish and trend_1 == c.Trend.Bearish:
        max_high = pointpos_df['high'].values.max()
        min_befor_max_high = np.where(np.logical_and(
            pointpos_df['pivot'] == 2, pointpos_df['high'] == max_high), pointpos_df.shift(1)['low'], -1).max()
        break_level=min_befor_max_high
        if df[-1:]['close'].values[0] < min_befor_max_high:
            pa_stat = c.PA_Break.Bullish_Break_Down
            isbreak = True
    del pointpos_df
    del df
    gc.collect()
    return pa_stat, isbreak,break_level


def are_close(num1, num2, threshold):
    minabs = min(abs(num1), abs(num2))
    if minabs == 0:
        return True
    return abs(num1 - num2) / minabs <= threshold


def close_nums(nums, threshold):

    # Sort the list of numbers
    nums.sort()

    # Initialize an empty list of groups
    groups = []

    # Initialize an empty group
    group = []

    # Loop through the list of numbers
    for num in nums:
        # If the group is empty or the current number is close to the last number in the group
        if not group or are_close(num, group[-1], threshold):
            # Add the current number to the group
            group.append(num)
        else:
            # Otherwise, add the current group to the list of groups and start a new group with the current number
            groups.append(group)
            group = [num]

    # Add the last group to the list of groups if it is not empty
    if group:
        groups.append(group)

    # Print the groups
    del nums
    gc.collect()
    return groups


def GetImportantLevels(df, threshold=0.01, combined=True):
    pointpos_df = pd.DataFrame(
        data=df[~pd.isnull(df['pointpos'])], columns=['pointpos', 'pivot'])
    if combined:
        pivots = pointpos_df['pointpos'].values
        groups = close_nums(nums=pivots, threshold=threshold)
        level_areas = []
        for g in groups:
            mean_g = mean(g)
            level_areas.append((mean_g*(1-threshold/2), mean_g*(1+threshold/2)))

        del pointpos_df
        del pivots
        gc.collect()
        return level_areas
    else:
        pivots_high = pointpos_df[pointpos_df['pivot'] == 2]['pointpos'].values
        pivots_low = pointpos_df[pointpos_df['pivot'] == 1]['pointpos'].values
        low_groups = close_nums(pivots_low, threshold)
        high_groups = close_nums(pivots_high, threshold)
        low_level_areas = []
        for g in low_groups:
            mean_g = mean(g)
            low_level_areas.append((mean_g*(1-threshold/2), mean_g*(1+threshold/2)))
        high_level_areas = []
        for g in high_groups:
            mean_g = mean(g)
            high_level_areas.append((mean_g*(1-threshold/2), mean_g*(1+threshold/2)))

        del pointpos_df
        del pivots_low
        del pivots_high

        gc.collect()
        return low_level_areas, high_level_areas


def GetIchiStatus(df):
    try:
        last_close = df[-1:]['close'].values[0]
        last_high = df[-1:]['high'].values[0]
        last_low = df[-1:]['low'].values[0]
        last_ichi_a = df[-1:]['ich_a'].values[0]
        last_ichi_b = df[-1:]['ich_b'].values[0]
        last_ichi_color = df[-1:]['ich_moku_color'].values[0]
        ichi_stat = c.Ichi_Stat.Nothing
        if (last_ichi_color < 0):  # red
            if (last_close <= last_ichi_a):
                ichi_stat = c.Ichi_Stat.Below_Red
            elif last_close >= last_ichi_b:
                ichi_stat = c.Ichi_Stat.Above_Red
            elif last_close >= last_ichi_a and last_close <= last_ichi_b:
                ichi_stat = c.Ichi_Stat.Inside_Red
        elif (last_ichi_color > 0):  # green
            if (last_close >= last_ichi_a):
                ichi_stat = c.Ichi_Stat.Above_Green
            elif last_close <= last_ichi_b:
                ichi_stat = c.Ichi_Stat.Below_Green
            elif last_close <= last_ichi_a and last_close >= last_ichi_b:
                ichi_stat = c.Ichi_Stat.Inside_Green

        del df
        gc.collect()
        return ichi_stat
    except:
        del df
        gc.collect()
        ichi_stat = c.Ichi_Stat.Error
        return ichi_stat


def double_levels(df, threshold=0.01):
    try:
        double_bot_level = 0
        double_top_level = 0
        pivots = pd.DataFrame(data=df[np.logical_or(df['pivot'] == 1, df['pivot'] == 2)], columns=[
                              'timestamp', 'low', 'high', 'pivot'])
        if (len(pivots) >= 5):
            last_pivot = pivots[-1:]

            last_low_pivot = last_pivot['low'].values[0]
            last_high_pivot = pivots[-2:-1]['high'].values[0]
            pre_last_low_pivot = pivots[-3:-2]['low'].values[0]
            pre_last_high_pivot = pivots[-4:-3]['high'].values[0]
            pre_pre_last_low_pivot = pivots[-5:-4]['low'].values[0]
            pre_pre_last_high_pivot = pivots[-5:-4]['high'].values[0]

            last_close = df[-1:]['close'].values[0]
            last_timestamp = df[-1:]['timestamp'].values[0]
            last_high_timestamp = pivots[-2:-1]['timestamp'].values[0]
            last_low_timestamp = pivots[-1:]['timestamp'].values[0]
            max_latest_candles_close = df[np.logical_and(
                df['timestamp'] > last_low_timestamp, df['timestamp'] < last_timestamp)]['close'].max()
            if (last_pivot['pivot'].values[0] == 1):
                if (pre_pre_last_low_pivot > pre_last_low_pivot and last_high_pivot < pre_last_high_pivot):
                    back_pct = round(
                        (last_high_pivot-pre_last_low_pivot)/(pre_last_high_pivot-pre_last_low_pivot)*100)
                    if back_pct >= 30:
                        low_pct = abs((last_low_pivot-pre_last_low_pivot) /
                                      ((pre_last_low_pivot+last_low_pivot)/2))
                        if low_pct <= threshold:
                            if (last_close < last_high_pivot and last_close > last_low_pivot and max_latest_candles_close < last_high_pivot and max_latest_candles_close > last_low_pivot):
                                double_bot_level = last_low_pivot
            else:

                min_latest_candles_close = df[np.logical_and(
                    df['timestamp'] > last_high_timestamp, df['timestamp'] < last_timestamp)]['close'].min()
                if (pre_pre_last_high_pivot < pre_last_high_pivot and last_low_pivot > pre_last_low_pivot):
                    back_pct = round(
                        (pre_last_high_pivot-last_low_pivot)/(pre_last_high_pivot-pre_last_low_pivot)*100)
                    if back_pct >= 30:
                        low_pct = abs((last_high_pivot-pre_last_high_pivot) /
                                      ((pre_last_high_pivot+last_high_pivot)/2))
                        if low_pct <= threshold:
                            if (last_close > last_low_pivot and last_close < last_high_pivot and min_latest_candles_close > last_low_pivot and min_latest_candles_close < last_high_pivot):
                                double_top_level = last_high_pivot

        del df
        del pivots
        gc.collect()
        return double_bot_level, double_top_level
    except:
        return 0, 0


def r2(comb):
    xs = [x[0] for x in comb]
    ys = [y[1] for y in comb]
    coeff = np.polyfit(x=xs, y=ys, deg=1)
    yn = np.poly1d(coeff)
    r2 = r2_score(ys, yn(xs))
    return r2


def ReturnTrend_From_Comb(comb, bounds):
    xs = [x[0] for x in comb]
    ys = [y[1] for y in comb]
    coeff = np.polyfit(x=xs, y=ys, deg=1)
    yn = np.poly1d(coeff)
    r2 = r2_score(ys, yn(xs))
    xs.insert(0, bounds[0])
    xs.append(bounds[1])
    return round(r2, 4), xs, yn(xs)


def Return_Combo(xs, ys, n, r_min):
    last_x = xs[-1]
    one_last_x=xs[-2:-1][0]
    # two_last_x=xs[-2:-1].values[0]
    combs = list(itertools.combinations(list(zip(xs, ys)), n))
    sorted_combs = sorted(combs, key=lambda c: r2(c), reverse=True)
    filtered_combs = [c for c in combs if c[-1][0] == last_x and one_last_x==c[-2][0] and r2(c) > r_min]
    if filtered_combs:
        # return the first element of filtered_combs as the best fitting combination
        return filtered_combs[0]
    else:
        # return the first element of sorted_combs as the best fitting combination
        return sorted_combs[0]


def Return_Trend_From_DF(df, r_min, n, mode=1):
    boudry_xs = [df.iloc[0].timestamp,
                 df.iloc[-1].timestamp]
    pointpos_df = pd.DataFrame(data=df[~pd.isnull(df['pointpos'])], columns=[
                               'time', 'pointpos', 'pivot', 'timestamp'])
    xs = list(
        (pointpos_df[pointpos_df['pivot'] == mode]['timestamp']).reset_index(drop=True))
    ys = list(
        (pointpos_df[pointpos_df['pivot'] == mode]['pointpos']).reset_index(drop=True))
    r2, trend_x, trend_y = ReturnTrend_From_Comb(
        Return_Combo(xs=xs, ys=ys, n=n, r_min=r_min), bounds=boudry_xs)
    m = (trend_y[-1]-trend_y[0]) / (trend_x[-1]-trend_x[0])
    del boudry_xs
    del pointpos_df
    del xs
    del ys
    del df
    gc.collect()
    return trend_x[0], trend_y[0], m, r2


def Candle_Dynamic_Trend_Stat(candle, supp_data,res_data,last_candles_diection, threshold=0.01, r_min=0.92):
    candle_support_stats=[]
    candle_resist_stats=[] 
    if last_candles_diection==c.Candles_Direction.Bearish:
        if supp_data['r2'] >= r_min:
            supp_last = supp_data['m']*(candle.timestamp - supp_data['p0_x'])+supp_data['p0_y']

            p_open_supp=(max(candle.open,supp_last)-min(candle.open,supp_last))/min(candle.open,supp_last)
            p_close_supp=(max(candle.close,supp_last)-min(candle.close,supp_last))/min(candle.close,supp_last)
            p_high_supp=(max(candle.high,supp_last)-min(candle.high,supp_last))/min(candle.high,supp_last)
            p_low_supp=(max(candle.low,supp_last)-min(candle.low,supp_last))/min(candle.low,supp_last)

            if p_close_supp <= threshold:
                candle_support_stats.append(c.Candle_Dynamic_SR_Stat.Close_Near_Support)
            if p_open_supp <= threshold:
                candle_support_stats.append(c.Candle_Dynamic_SR_Stat.Open_Near_Support)
            if p_high_supp <= threshold or p_low_supp <=threshold:
                candle_support_stats.append(c.Candle_Dynamic_SR_Stat.Shadow_Near_Support)
    elif last_candles_diection==c.Candles_Direction.Bullish:
        if res_data['r2'] >= r_min:
            res_last = res_data['m']*(candle.timestamp - res_data['p0_x'])+res_data['p0_y']

            p_open_res=(max(candle.open,res_last)-min(candle.open,res_last))/min(candle.open,res_last)
            p_close_res=(max(candle.close,res_last)-min(candle.close,res_last))/min(candle.close,res_last)
            p_high_res=(max(candle.high,res_last)-min(candle.high,res_last))/min(candle.high,res_last)
            p_low_res=(max(candle.low,res_last)-min(candle.low,res_last))/min(candle.low,res_last)

            if p_close_res <= threshold:
                candle_resist_stats.append(c.Candle_Dynamic_SR_Stat.Close_Near_Resist)
            if p_open_res <= threshold:
                candle_resist_stats.append(c.Candle_Dynamic_SR_Stat.Open_Near_Resist)
            if p_high_res<= threshold or p_low_res <=threshold:
                candle_resist_stats.append(c.Candle_Dynamic_SR_Stat.Shadow_Near_Resist)

    return candle_support_stats, candle_resist_stats


def Dynamic_SR(df,last_candles_diection, threshold=0.01, r_min=0.92, n=3):
    try:

        R_stat = c.Trend_SR_Stat.Nothing
        S_stat = c.Trend_SR_Stat.Nothing
        candle_support_stats = []
        candle_resist_stats = []

        p0_sup_x, p0_sup_y, m_sup, r2_sup = Return_Trend_From_DF(
            df, r_min, n, 1)
        dict_sup={'p0_x':p0_sup_x,'p0_y':p0_sup_y,'m':m_sup,'r2':r2_sup}
        p0_res_x, p0_res_y, m_res, r2_res = Return_Trend_From_DF(
            df, r_min, n, 2)
        dict_res={'p0_x':p0_res_x,'p0_y':p0_res_y,'m':m_res,'r2':r2_res}

        candle_support_stats, candle_resist_stats = Candle_Dynamic_Trend_Stat(candle=df.iloc[-1], supp_data=dict_sup,res_data=dict_res, r_min=r_min,last_candles_diection=last_candles_diection, threshold=threshold)

        if r2_sup >= r_min:
            S_stat = c.Trend_SR_Stat.Fit_Support

        if r2_res >= r_min:
            R_stat = c.Trend_SR_Stat.Fit_Resist
        del df

        gc.collect()
        return S_stat, candle_support_stats, R_stat, candle_resist_stats

    except:
        del df
        gc.collect()
        print(f'Error occured')
        return 'Error on Trend Status'

8
def FiboStat(df, fibomode=c.Fibo_Mode.Retracement, threshold=0.01):
    stat = c.Candle_Fibo_Stat.Nothing
    dir = c.Fibo_Direction.Up
    pivots = pd.DataFrame(data=df[np.logical_or(df['pivot'] == 1, df['pivot'] == 2)], columns=[
        'timestamp', 'low', 'high', 'pivot'])
    fibs = [0, 0.382, 0.5, 0.618, 0.786, 1, 1.618, 2.618]
    levels=[]
    if (len(pivots) >= 3):
        last_pivot = pivots[-1:]

        last_low_pivot = last_pivot['low'].values[0]
        last_high_pivot = pivots[-2:-1]['high'].values[0]
        pre_last_low_pivot = pivots[-3:-2]['low'].values[0]
        pre_last_high_pivot = pivots[-4:-3]['high'].values[0]
        last_close = df[-1:]['close'].values[0]

        if (last_pivot['pivot'].values[0] == 1):
            if fibomode == c.Fibo_Mode.Retracement:
                h = last_high_pivot-last_low_pivot
            else:
                h = last_high_pivot-pre_last_low_pivot

            for f in range(0, len(fibs)):
                level = fibs[f]*h+last_low_pivot
                levels.append(level)
                ratio = last_close/level
                if abs(1-ratio) <= threshold:
                    stat = c.Candle_Fibo_Stat(f)
                    dir=c.Fibo_Direction.Up
        else:
            if fibomode == c.Fibo_Mode.Retracement:
                h = last_low_pivot-last_high_pivot
            else:
                h = last_low_pivot-pre_last_high_pivot

            for f in range(0, len(fibs)):
                level = fibs[f]*h+last_high_pivot
                levels.append(level)
                ratio = last_close/level
                if abs(1-ratio) <= threshold:
                    stat = c.Candle_Fibo_Stat(f)
                    dir=c.Fibo_Direction.Down

    del fibs
    del pivots
    gc.collect()
    return dir,stat,levels

def Candles_direction(candles):
    xs=[]
    ys=[]
    for i in range(0,len(candles)):
        xs.append(candles['timestamp'][i])
        ys.append(candles['close'][i])
    _,ys_fit=ReturnTrend(xs,ys)
    if ys_fit[-1]>ys_fit[0]:
        return c.Candles_Direction.Bullish
    elif ys_fit[-1]<ys_fit[0]:
        return c.Candles_Direction.Bearish
    else:
        return c.Candles_Direction.Side


def Candle_level_stat(level_top, level_bot, candle, last_candles_diection, threshold=0.015):
    stats=[]
    if last_candles_diection==c.Candles_Direction.Bullish:
        if candle.close >= candle.open:  # green candle
            if candle.close <= level_top and candle.close >= level_bot:
                stats.append(c.Candle_Level_Area_Stat.Closed_In_Resist)
            elif candle.close <= level_bot:
                p=(level_bot-candle.close)/candle.close
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Closed_Near_Resist)
            elif candle.close >= level_top:
                p=(candle.close-level_top)/level_top
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Closed_Near_Resist)
        else:
            if candle.open <= level_top and candle.open >= level_bot:
                stats.append(c.Candle_Level_Area_Stat.Closed_In_Resist)
            elif candle.open <= level_bot:
                p=(level_bot-candle.open)/candle.open
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Opened_Near_Resist)
            elif candle.open >= level_top:
                p=(candle.open-level_top)/level_top
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Opened_Near_Resist)
        if (candle.high <= level_top and candle.high >= level_bot): 
            stats.append( c.Candle_Level_Area_Stat.Shadow_In_Resist)
        elif candle.high < level_bot:
            p=(level_bot-candle.high)/candle.high
            if p<=threshold/2:
                stats.append(c.Candle_Level_Area_Stat.Shadow_Near_Resist)   
    elif last_candles_diection==c.Candles_Direction.Bearish:
        if candle.close >= candle.open:  # green candle
            if candle.open <= level_top and candle.open >= level_bot:
                stats.append(c.Candle_Level_Area_Stat.Opened_In_Support)
            elif candle.close <= level_bot:
                p=(level_bot-candle.close)/candle.close
                if p<=threshold:
                    stats.append(c.Candle_Level_Area_Stat.Opened_Near_Support)
            elif candle.close >= level_top:
                p=(candle.close-level_top)/level_top
                if p<=threshold:
                    stats.append(c.Candle_Level_Area_Stat.Opened_Near_Support)
        else:
            if candle.open <= level_top and candle.open >= level_bot:
                stats.append(c.Candle_Level_Area_Stat.Closed_In_Support)
            elif candle.open <= level_bot:
                p=(level_bot-candle.open)/candle.open
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Closed_Near_Support)
            elif candle.open >= level_top:
                p=(candle.open-level_top)/level_top
                if p<=threshold/2:
                    stats.append(c.Candle_Level_Area_Stat.Closed_Near_Support)
        if(candle.low <= level_top and candle.low >= level_bot):
            stats.append( c.Candle_Level_Area_Stat.Shadow_In_Support)
        elif candle.low > level_top:
            p=(candle.low-level_top)/level_top
            if p<=threshold/2:
                stats.append(c.Candle_Level_Area_Stat.Shadow_Near_Support)

    
    return stats

def Candle_fibo_levle_stat(candle, levels,tf,thb=1):
    stat=c.Candle_Fibo_Stat.Nothing
    fibs = [0, 0.382, 0.5, 0.618, 0.786, 1, 1.618, 2.618]
    th=threshold(tf,thb)
    for f in range(0,len(fibs)):
        ratio=candle.close/levels[f]
        if abs(1-ratio) <= th:
            stat = c.Candle_Fibo_Stat(f)
            return stat
    return stat

def Candle_Shapes(candle,th=0.01):
    shapes=[]
    if abs(1-candle.high/candle.low)<=th : 
        shapes.append(c.Candle_Shape.Small)
    if abs(1-candle.high/candle.low)<=3*th : 
        shapes.append(c.Candle_Shape.Normal)

    if abs(1-candle.close/candle.open)<=th:
        shapes.append(c.Candle_Shape.Point)
    
    tot_h=candle.high-candle.low
    h_2_3=2.0/3.0*tot_h

    if candle.close>candle.open:
        if candle.open-candle.low>h_2_3:
            shapes.append(c.Candle_Shape.PinBar_Up)
        elif candle.high-candle.close>h_2_3:
            shapes.append(c.Candle_Shape.PinBar_Down)
    else:
        if candle.close-candle.low>h_2_3:
            shapes.append(c.Candle_Shape.PinBar_Up)
        elif candle.high-candle.open>h_2_3:
            shapes.append(c.Candle_Shape.PinBar_Down)
    
    return shapes