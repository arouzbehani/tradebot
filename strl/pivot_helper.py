import pandas as pd
import numpy as np
import gc
def lows_highs_1(values, timestamps):
    lows = []
    highs = []
    for i in range(len(values)):
        if i == 0:
            lows.append((timestamps[i], values[i]))
            highs.append((timestamps[i], values[i]))
        else:
            if values[i] < lows[-1][1]:
                lows.append((timestamps[i], values[i]))
            elif values[i] > highs[-1][1]:
                highs.append((timestamps[i], values[i]))
    return lows, highs
def lows_highs(values, timestamps,candles=3):
    lows = []
    highs = []
    lows.append(((timestamps[0], values[0]),0))
    highs.append(((timestamps[0], values[0]),0))
    
    j=candles

    for i in range(1,len(values)-1):
        if values[i]<values[i+1:i+j+1].min():
            if i>=j and values[i] < values[i-j:i].min():
                if(i==lows[-1][1]):
                    if(values[i]<lows[-1][0][1]):
                        lows[-1]=((timestamps[i],values[i]),i)
                    else:
                        lows.append(((timestamps[i],values[i]),i))
                else:
                    lows.append(((timestamps[i],values[i]),i))
        elif values[i]>values[i+1:i+j+1].max():
            if i>=j and values[i] > values[i-j:i].max():
                if(i==highs[-1][1]):
                    if(values[i]>highs[-1][0][1]):
                        highs[-1]=((timestamps[i],values[i]),i)
                    else:
                        highs.append(((timestamps[i],values[i]),i))
                else:
                    highs.append(((timestamps[i],values[i]),i))


    return lows, highs

def pivotid(df1, l, n1, n2):
    if l-n1 < 0 :
        return 0
    # if l+n2>=len(df1):
    #     if  l+3 >= len(df1):
    #         return 0
    #     else:
    #         n2=3
    pividlow = 1
    pividhigh = 1
    limit1=l-n1
    limit2=l+n2+1
    if l+n2>=len(df1):
        if l+max(int(n2/3.5),6)>=len(df1):
            return 0
        else:
            limit2=l+max(int(n2/3.5),6)+1
    for i in range(limit1, limit2):
        if (df1.low[l] > df1.low[i]):
            pividlow = 0
        if (df1.high[l] < df1.high[i]):
            pividhigh = 0
    if pividhigh and pividlow:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0


def pointpos(x):

    if x['pivot'] == 1:
        return x['low']
    if x['pivot'] == 2:
        return x['high']
    else:
        return np.nan


def trendstat(df1, l, short=False):
    if (short):
        return np.nan
    if (l >= 3):
        if (df1.loc[l].pivot == 1):
            if (df1.loc[l].low > df1.loc[l-2].low and df1.loc[l-1].high > df1.loc[l-3].high):

                return "up"
            elif df1.loc[l].low < df1.loc[l-2].low and df1.loc[l-1].high < df1.loc[l-3].high:
                return "down"
            else:
                return 'side'
        if (df1.loc[l].pivot == 2):
            if (df1.loc[l].high > df1.loc[l-2].high and df1.loc[l-1].low > df1.loc[l-3].low):
                return "up"
            if (df1.loc[l].high < df1.loc[l-2].high and df1.loc[l-1].low < df1.loc[l-3].low):
                return "down"
            else:
                return 'side'
    else:
        return np.nan


def calcualte_power_points_up(df1, l, wn, pivot=1):
    depth_point = 0
    dist_point = 0
    velocity_point = 0
    depths = []
    distances = []
    slope_downs = []
    slope_ups = []
    if (pivot == 1):  # l index low
        for x in range(1, 2*wn, 2):
            depths.append(
                (df1.loc[l-x].high-df1.loc[l-x+1].low)/df1.loc[l-x+1].low*100)
        for x in range(1, 2*wn-2, 2):
            distances.append(df1.loc[l-x].high-df1.loc[l-x-2].high)
        for x in range(0, 2*wn-1, 2):
            slope_downs.append((df1.loc[l-x-1].high-df1.loc[l-x].low) /
                               (df1.loc[l-x].timestamp-df1.loc[l-x-1].timestamp))
            slope_ups.append((df1.loc[l-x-1].high-df1.loc[l-x-2].low) /
                             (df1.loc[l-x-1].timestamp-df1.loc[l-x-2].timestamp))
    else:  # l index high
        for x in range(1, 2*wn, 2):
            depths.append(
                (df1.loc[l-x-1].high-df1.loc[l-x].low)/df1.loc[l-x].low*100)
        for x in range(2, 2*wn+1, 2):
            distances.append(df1.loc[l-x].high-df1.loc[l-x+2].high)
        for x in range(0, 2*wn-1, 2):
            slope_downs.append((df1.loc[l-x-2].high-df1.loc[l-x-1].low) /
                               (df1.loc[l-x-1].timestamp-df1.loc[l-x-2].timestamp))
            slope_ups.append((df1.loc[l-x].high-df1.loc[l-x-1].low) /
                             (df1.loc[l-x].timestamp-df1.loc[l-x-1].timestamp))
    for x in range(0, len(depths)-1):
        if (depths[x] <= depths[x+1]):
            depth_point += 1*(1-0.1*x)
        else:
            depth_point -= 1*(1-0.1*x)
    for x in range(0, len(distances)-1):
        if (distances[x] >= distances[x+1]):
            dist_point += 1*(1-0.1*x)
        else:
            dist_point -= 1*(1-0.1*x)
    if slope_downs[0] < slope_ups[0]:
        velocity_point += 1
    else:
        velocity_point -= 1
    for x in range(0, len(slope_downs)-1):
        if (slope_downs[x] <= slope_downs[x+1]):
            velocity_point += 1*(1-0.1*x)
    for x in range(0, len(slope_ups)-1):
        if (slope_ups[x] >= slope_ups[x+1]):
            velocity_point += 1*(1-0.1*x)
    return velocity_point, depth_point, dist_point


def calcualte_power_points_down(df1, l, wn, pivot=1):
    depth_point = 0
    dist_point = 0
    velocity_point = 0
    depths = []
    distances = []
    slope_downs = []
    slope_ups = []
    if (pivot == 1):  # l index low
        for x in range(1, 2*wn, 2):
            depths.append(
                (df1.loc[l-x].high-df1.loc[l-x-1].low)/df1.loc[l-x-1].low*100)
        for x in range(1, 2*wn-2, 2):
            distances.append(df1.loc[l-x-2].high-df1.loc[l-x].high)
        for x in range(0, 2*wn, 2):
            slope_downs.append((df1.loc[l-x-1].high-df1.loc[l-x].low) /
                               (df1.loc[l-x].timestamp-df1.loc[l-x-1].timestamp))
            slope_ups.append((df1.loc[l-x-1].high-df1.loc[l-x-2].low) /
                             (df1.loc[l-x-1].timestamp-df1.loc[l-x-2].timestamp))
    else:  # l index high
        for x in range(1, 2*wn, 2):
            depths.append(
                (df1.loc[l-x-1].high-df1.loc[l-x].low)/df1.loc[l-x].low*100)
        for x in range(2, 2*wn+1, 2):
            distances.append(df1.loc[l-x].high-df1.loc[l-x+2].high)
        for x in range(0, 2*wn, 2):
            slope_downs.append((df1.loc[l-x-2].high-df1.loc[l-x-1].low) /
                               (df1.loc[l-x-1].timestamp-df1.loc[l-x-2].timestamp))
            slope_ups.append((df1.loc[l-x].high-df1.loc[l-x-1].low) /
                             (df1.loc[l-x].timestamp-df1.loc[l-x-1].timestamp))
    for x in range(0, len(depths)-1):
        if (depths[x] <= depths[x+1]):
            depth_point += 1*(1-0.1*x)
        else:
            depth_point -= 1*(1-0.1*x)
    for x in range(0, len(distances)-1):
        if (distances[x] >= distances[x+1]):
            dist_point += 1*(1-0.1*x)
        else:
            dist_point -= 1*(1-0.1*x)
    if slope_downs[0] > slope_ups[0]:
        velocity_point += 1
    else:
        velocity_point -= 1
    for x in range(0, len(slope_downs)-1):
        if (slope_downs[x] <= slope_downs[x+1]):
            velocity_point += 1*(1-0.1*x)
    for x in range(0, len(slope_ups)-1):
        if (slope_ups[x] >= slope_ups[x+1]):
            velocity_point += 1*(1-0.1*x)
    return velocity_point, depth_point, dist_point


def powerstat(df1, l, wn=3, short=False):
    # wn: Number of Waves
    # l: candles index
    # df1 Filtered Dataframe with only rows having pivot 1 or 2
    if short:
        return np.nan
    if (l >= 2*wn):
        if (df1.loc[l].pivot == 1):
            uptrend_cond = True
            for x in range(0, 2*wn-2, 2):
                if (df1.loc[l-x].low < df1.loc[l-x-2].low or df1.loc[l-x-1].high < df1.loc[l-x-3].high):
                    uptrend_cond = False
                    break
            if (df1.loc[l-2*wn+2].low < df1.loc[l-2*wn].low):
                uptrend_cond = False

            if (uptrend_cond):
                velocity_point, depth_point, dist_point = calcualte_power_points_up(
                    df1, l, wn, pivot=1)
                if (dist_point+depth_point+velocity_point > 0):
                    return "strong up"
                elif dist_point+depth_point+velocity_point < 0:
                    return "weak up"
                else:
                    return np.nan

            else:
                downtrend_cond = True
                for x in range(0, 2*wn-2, 2):
                    if (df1.loc[l-x].low > df1.loc[l-x-2].low or df1.loc[l-x-1].high > df1.loc[l-x-3].high):
                        downtrend_cond = False
                        break

                if (df1.loc[l-2*wn+2].low > df1.loc[l-2*wn].low):
                    downtrend_cond = False

                if (downtrend_cond):
                    velocity_point, depth_point, dist_point = calcualte_power_points_down(
                        df1, l, wn, pivot=1)
                    if (dist_point+depth_point+velocity_point > 0):
                        return "strong down"
                    elif dist_point+depth_point+velocity_point < 0:
                        return "weak down"
                    else:
                        return np.nan
                else:
                    return np.nan

        if (df1.loc[l].pivot == 2):
            uptrend_cond = True
            for x in range(0, 2*wn-2, 2):
                if (df1.loc[l-x].high < df1.loc[l-x-2].high or df1.loc[l-x-1].low < df1.loc[l-x-3].low):
                    uptrend_cond = False
                    break
            if (df1.loc[l-2*wn+2].high < df1.loc[l-2*wn].high):
                uptrend_cond = False

            if (uptrend_cond):
                velocity_point, depth_point, dist_point = calcualte_power_points_up(
                    df1, l, wn, pivot=2)
                if (dist_point+depth_point+velocity_point > 0):
                    return "strong up"
                elif dist_point+depth_point+velocity_point < 0:
                    return "weak up"
                else:
                    return np.nan

            else:
                downtrend_cond = True
                for x in range(0, 2*wn-2, 2):
                    if (df1.loc[l-x].high > df1.loc[l-x-2].high or df1.loc[l-x-1].low > df1.loc[l-x-3].low):
                        downtrend_cond = False
                        break
                if (df1.loc[l-2*wn+2].high > df1.loc[l-2*wn].high):
                    downtrend_cond = False

                if (downtrend_cond):
                    velocity_point, depth_point, dist_point = calcualte_power_points_down(
                        df1, l, wn, pivot=1)
                    if (dist_point+depth_point+velocity_point > 0):
                        return "strong down"
                    elif dist_point+depth_point+velocity_point < 0:
                        return "weak down"
                    else:
                        return np.nan
                else:
                    return np.nan

    else:
        return np.nan
    return np.nan


pd.options.mode.chained_assignment = None  # default='warn'


def find_pivots_new(df, left_candles=7, right_candles=7, wn=2, short=False):
    _,highs=lows_highs(df['high'].values,df['timestamp'],left_candles)
    lows,_=lows_highs(df['low'].values,df['timestamp'],left_candles)
    df['init_pivot'] = 0
    low_t_values = set([x[0][0] for x in lows])
    high_t_values = set([x[0][0] for x in highs])
    df['pivot'] = df['timestamp'].apply(lambda x: 1 if x in low_t_values else 2 if x in high_t_values else 0)

    df2 = df.loc[np.logical_or(
        df['pivot'] == 1, df['pivot'] == 2)].reset_index()
    df2['pivot_trend'] = df2.apply(
        lambda x: trendstat(df2, x.name, short=short), axis=1)
    df2['pivot_power'] = df2.apply(lambda x: powerstat(
        df2, x.name, wn, short=short), axis=1)

    df['pivot_trend'] = np.nan
    df['pivot_power'] = np.nan

    for r in range(0, len(df2)):
        df.loc[df2.loc[r]['index']] = df2.loc[r]
    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)

    if short:
        del df2
        gc.collect()
        return df

    up_points = np.where(df['pivot_trend'] == 'up', df['pointpos'], np.nan)
    down_points = np.where(df['pivot_trend'] == 'down', df['pointpos'], np.nan)
    sidepoints = np.where(df['pivot_trend'] == 'side', df['pointpos'], np.nan)
    power_up_points = np.where(
        df['pivot_power'] == 'strong up', df['pointpos'], np.nan)
    power_down_points = np.where(
        df['pivot_power'] == 'strong down', df['pointpos'], np.nan)
    power_weaking_up_points = np.where(
        df['pivot_power'] == 'weak up', df['pointpos'], np.nan)
    power_weaking_down_points = np.where(
        df['pivot_power'] == 'weak down', df['pointpos'], np.nan)

    return df, up_points, down_points, sidepoints, power_up_points, power_down_points, power_weaking_up_points, power_weaking_down_points

def find_pivots(df, left_candles=7, right_candles=7, wn=2, short=False):
    df['init_pivot'] = df.apply(lambda x: pivotid(
        df, x.name, left_candles, right_candles), axis=1)
    df['pivot'] = np.nan
    i = 0
    while i < len(df)-1:
        if (df['init_pivot'][i] == 1):
            df['pivot'][i] = 1
            for j in range(i+1, len(df)):
                if df['init_pivot'][j] == 1:
                    if df['low'][j] <= df['low'][i]:
                        df['pivot'][i:j] = np.nan
                        df['pivot'][j] = 1
                elif df['init_pivot'][j] == 2:
                    i = j
                    break
            if j == len(df)-1:
                break
        elif df['init_pivot'][i] == 2:
            df['pivot'][i] = 2
            for j in range(i+1, len(df)):
                if df['init_pivot'][j] == 2:
                    if df['high'][j] >= df['high'][i]:
                        df['pivot'][i:j] = np.nan
                        df['pivot'][j] = 2
                elif df['init_pivot'][j] == 1:
                    i = j
                    break
            if j == len(df)-1:
                break
        else:
            i += 1
    df2 = df.loc[np.logical_or(
        df['pivot'] == 1, df['pivot'] == 2)].reset_index()
    df2['pivot_trend'] = df2.apply(
        lambda x: trendstat(df2, x.name, short=short), axis=1)
    df2['pivot_power'] = df2.apply(lambda x: powerstat(
        df2, x.name, wn, short=short), axis=1)

    df['pivot_trend'] = np.nan
    df['pivot_power'] = np.nan

    for r in range(0, len(df2)):
        df.loc[df2.loc[r]['index']] = df2.loc[r]
    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)

    if short:
        del df2
        gc.collect()
        return df

    up_points = np.where(df['pivot_trend'] == 'up', df['pointpos'], np.nan)
    down_points = np.where(df['pivot_trend'] == 'down', df['pointpos'], np.nan)
    sidepoints = np.where(df['pivot_trend'] == 'side', df['pointpos'], np.nan)
    power_up_points = np.where(
        df['pivot_power'] == 'strong up', df['pointpos'], np.nan)
    power_down_points = np.where(
        df['pivot_power'] == 'strong down', df['pointpos'], np.nan)
    power_weaking_up_points = np.where(
        df['pivot_power'] == 'weak up', df['pointpos'], np.nan)
    power_weaking_down_points = np.where(
        df['pivot_power'] == 'weak down', df['pointpos'], np.nan)

    return df, up_points, down_points, sidepoints, power_up_points, power_down_points, power_weaking_up_points, power_weaking_down_points
