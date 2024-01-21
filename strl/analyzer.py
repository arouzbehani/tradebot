
import gc

import numpy as np
import helper
import Constants as c , analaysis_constants as ac
import pivot_helper
import situations as s
import pandas as pd
class Analyzer:
    def __init__(self):
        self.tfs=['1d', '4h', '1h', '15m']
        self.trend_limit_long=ac.Long_Term_Trend_Limit
        self.trend_limit_short=ac.Short_Term_Trend_Limit
        self.long_term_pivot_candles=ac.Long_Term_Candles
        self.short_term_pivot_candles=ac.Short_Term_Candles
        self.waves_number=ac.PA_Power_Calc_Waves
        self.pvt_trend_number=ac.Pivot_Trend_Number
        self.analysis='1.0'
        self.symbol='BTC_USDT'
        self.exch='Kucoin'
        self.dict={}
        self.situations={}
        self.threshold=ac.Threshold/100

    def init_data(self,tfs=['1d', '4h', '1h', '15m'],trend_limit_long=ac.Long_Term_Trend_Limit,trend_limit_short=ac.Short_Term_Trend_Limit,
                  long_term_pivot_candles=ac.Long_Term_Candles,short_term_pivot_candles=ac.Short_Term_Candles,
                  waves_number=ac.PA_Power_Calc_Waves,pvt_trend_number=ac.Pivot_Trend_Number,
             analysis='1.0',symbol='BTC_USDT',exch='Kucoin',candles_back=0,th=ac.Threshold/100):
        self.tfs=tfs
        self.trend_limit_long=trend_limit_long
        self.trend_limit_short=trend_limit_short
        self.long_term_pivot_candles=long_term_pivot_candles
        self.short_term_pivot_candles=short_term_pivot_candles
        self.waves_number=waves_number
        self.pvt_trend_number=pvt_trend_number
        self.analysis=analysis
        self.symbol=symbol
        self.exch=exch
        self.threshold=th
        self.calculate_dict(candles_back=candles_back)
        self.calculate_situations()
        
    def adjust_threshold(self,tf):
        rs={'1w':0.2,'1d':0.5,'1day':0.5,'4h':1.0,'4Hour':1.0,'90m':1.5,'1h':2.0,'1Hour':2.0,'60m':2.0,'15m':4,'15min':4,'5m':6,'5min':6,'1m':10,'1min':10}
        return self.threshold/rs[tf] 
    def calculate_dict(self,candles_back=0):
        if self.analysis == '1.0':
            for tf in self.tfs:
                candles_back_copy=candles_back
                adj_th=self.adjust_threshold(tf)
                df = helper.GetData(tf, self.symbol, self.exch)
                if df is None: continue
                if len(df)<ac.Long_Term_Trend_Limit:
                    self.trend_limit_long=len(df)
                if candles_back < 0:
                    candles_back_copy = len(df) - self.trend_limit_long
                elif candles_back>0:
                    if candles_back > len(df) - self.trend_limit_long:
                        candles_back_copy = len(df) - self.trend_limit_long

                helper.append_ichi(df)
                df_long = df[len(df)-self.trend_limit_long-candles_back_copy:len(df)-candles_back_copy].reset_index(drop=True)
                
                df_short = df[len(df)-self.trend_limit_short-candles_back_copy:len(df)-candles_back_copy].reset_index(drop=True)
                df_long = pivot_helper.find_pivots(
                    df_long, self.long_term_pivot_candles, self.long_term_pivot_candles, self.waves_number, short=True)
                df_short = pivot_helper.find_pivots(
                    df_short, self.short_term_pivot_candles, self.short_term_pivot_candles, 2, short=True)
                helper.append_sma_2(df_short,entry_signal=False,w1=10,w2=50)
                sma_stat=helper.Candle_SMA_Stat(candle=df_short.iloc[-1])==c.SMA_Stat.CrossUp
                helper.append_ema(df_short,entry_signal=True,entry_signal_mode='',exit_signal=True)
                ema_entry_signal=not pd.isna(df_short.iloc[-1].ema_entry_signal)
                ema_exit_signal=not pd.isna(df_short.iloc[-1].ema_exit_signal)
                helper.append_ema_W(df_long,window=150)
                ema_150_trend=c.Trend.Nothing
                if df_long.iloc[-1].close >df_long.iloc[-1].ema_150:
                    ema_150_trend=c.Trend.Bullish
                elif df_long.iloc[-1].close <df_long.iloc[-1].ema_150:
                    ema_150_trend=c.Trend.Bearish
                    
                trend_long,long_up_points,long_down_points = helper.TrendDirection(df_long)
                trend_short,short_up_points,short_down_points = helper.TrendDirection(df_short)
                pa_break, is_break,break_level = helper.PA_Break(
                    df_long, trend_long, trend_short)
                
                # major pivots in short term period:
                df_levels=df_long[len(df_long)-self.trend_limit_short-candles_back_copy:len(df_long)-candles_back_copy].reset_index(drop=True)
                static_levels = helper.GetImportantLevels(
                    df_levels, threshold=adj_th*2, combined=True)

                ichi_status = helper.GetIchiStatus(df_short)
                has_bermuda,bermuda_location,bermuda_distance,min_ichi,max_ichi=helper.has_Ichi_Bermuda(df_short)
                helper.append_rsi(df_short)
                rsi_data={"dvg":c.Rsi_Stat.Nothing,"chart_line":[],"rsi_line":[]}
                rsi_dvg,chart_xs,chart_ys,rsi_xs,rsi_ys=helper.Rsi_Divergence_3(df_short)
                if rsi_dvg:
                    rsi_data['chart_line']=[chart_xs,chart_ys]
                    rsi_data['rsi_line']=[rsi_xs,rsi_ys]
                    if rsi_ys[1]>rsi_ys[0]>0:
                        rsi_data['dvg']=c.Rsi_Stat.Up
                    else:
                        rsi_data['dvg']=c.Rsi_Stat.Down
                rsi_data['over_75']=df_short.iloc[-1].rsi>=75
                rsi_data['below_30']=df_short.iloc[-1].rsi<=30
                rsi_data['rsi']=df_short.iloc[-1].rsi
                db_bot, db_top = helper.double_levels(df_long, threshold=adj_th)

                helper.append_bb(df_short)
                last_candle=df_short.iloc[-1]
                bollinger_data={"upper":
                                {"close":last_candle.upperband-last_candle.close,
                                  "open":last_candle.upperband-last_candle.open,
                                  "high":last_candle.upperband-last_candle.high,
                                  "low":last_candle.upperband-last_candle.low},
                                "lower":
                                {"close":last_candle.lowerband-last_candle.close,
                                  "open":last_candle.lowerband-last_candle.open,
                                  "high":last_candle.lowerband-last_candle.high,
                                  "low":last_candle.lowerband-last_candle.low}
                                  }
                current_trend=c.Trend.Nothing
                if trend_long == c.Trend.Bullish:
                    if (trend_short == c.Trend.Bearish and is_break):
                        current_trend=c.Trend.Bearish
                    elif (trend_short==c.Trend.Bullish):
                        current_trend=c.Trend.Bullish
                elif trend_long == c.Trend.Bearish:
                    if (trend_short == c.Trend.Bullish and is_break):
                        current_trend=c.Trend.Bullish
                    elif (trend_short == c.Trend.Bearish):
                        current_trend=c.Trend.Bearish

                last_candles=df_short[-ac.Latest_Candles_Direction:].reset_index(drop=True)
                last_candles_diection=helper.Candles_direction(last_candles)

                # "S" stands for "Supoort" "R" stands for "Resistance"
                # S_stat,candle_S_stats,R_stat,candle_R_stats,candle_location=helper.Dynamic_SR(df=df_short,threshold=adj_th,n=self.pvt_trend_number)
                # p0_sup_x,p0_sup_y,m_sup,r2_sup=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=self.pvt_trend_number,mode=1)
                # p0_res_x,p0_res_y,m_res,r2_res=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=self.pvt_trend_number,mode=2)

                # *_long stands for df_long (long term : 280 candles and 16 candles left/right)
                pivots = pd.DataFrame(
                    data=df_long[np.logical_or(df_long["pivot"] == 1, df_long["pivot"] == 2)],
                    columns=["row_index", "low", "high", "pivot"],
                )
                last_pivot = pivots[-1:]
                last_pivots=[]
                last_pivots.append(last_pivot)
                last_pivots.append(pivots[-2:-1])                
                last_pivots.append(pivots[-3:-2])                
                remaining_candles=df_long[-len(df_long)+last_pivot.index.values[0]+1:-1].reset_index(drop=True)         
                      #sit.parent_dynamic_support_stats,sit.parent_dynamic_resist_stats,candle_location=helper.Candle_Dynamic_Trend_Stat(candle=candle,supp_data=dict[tf_p]['support_dynamic_trend'],res_data=dict[tf_p]['resist_dynamic_trend'],r_min=0.95,last_candles_diection=sit.last_candles_diection, threshold=adj_th)

                S_long_stat,candle_S_long_stats,R_long_stat,candle_R_long_stats,candle_location_long=helper.Dynamic_SR(df=df_long,remaining_candles=remaining_candles,candle=df_long.iloc[-1], threshold=adj_th,n=self.pvt_trend_number)
                p0_sup_long_x,p0_sup_long_y,m_sup_long,r2_sup_long=helper.Return_Trend_From_DF(df_long,r_min=0.95,n=self.pvt_trend_number,mode=1)
                p0_res_long_x,p0_res_long_y,m_res_long,r2_res_long=helper.Return_Trend_From_DF(df_long,r_min=0.95,n=self.pvt_trend_number,mode=2)

                fibo_dir_retrace,fibo_stat_retrace,fibo_retrace_levels=helper.FiboStat(df=df_long,fibomode=c.Fibo_Mode.Retracement,threshold=adj_th,max_remaining_candles=ac.Long_Term_Candles)
                fibo_dir_trend,fibo_stat_trend,fibo_trend_levels=helper.FiboStat(df=df_long,fibomode=c.Fibo_Mode.Trend_Base_Extension,threshold=adj_th,max_remaining_candles=ac.Long_Term_Candles)
                fibo_data_retrace={'dir':fibo_dir_retrace,'stat':fibo_stat_retrace,'levels':fibo_retrace_levels}
                fibo_data_trend={'dir':fibo_dir_trend, 'stat':fibo_stat_trend,'levels':fibo_trend_levels}
                last_candle_color=c.Candle_Color.Red
                last_candle=df_short.iloc[-1]

                if last_candle.close>last_candle.open:
                    last_candle_color=c.Candle_Color.Green


                self.dict[tf] = {'last_candle_color':last_candle_color, 
                            'df_long':df_long,'df_short':df_short,
                            'long_trend': trend_long,'long_trend_points':[long_up_points,long_down_points],
                            'short_trend': trend_short,'short_trend_points':[short_up_points,short_down_points],
                            'current_trend':current_trend,
                            'last_candles_diection':last_candles_diection,
                            'ichi_bermuda':{'hasbermuda':has_bermuda,'location':bermuda_location,'distance':bermuda_distance,'min_val':min_ichi,'max_val':max_ichi},
                            'pa_break': pa_break, 'is_break': is_break, 'break_level':break_level,

                            'static_levels': static_levels,

                            'ichi_stat': ichi_status, 'double_bot_level': db_bot,'double_top_level': db_top,

                            'fibo':{'retrace':fibo_data_retrace,'trend':fibo_data_trend},

                            # 'support_dynamic_trend':{'p0_x':p0_sup_x,'p0_y':p0_sup_y,'m':m_sup,'r2':r2_sup},
                            # 'resist_dynamic_trend':{'p0_x':p0_res_x,'p0_y':p0_res_y,'m':m_res,'r2':r2_res},
                            # 'dynamic_support':{'trend_stat':S_stat,'candle_stat':candle_S_stats},
                            # 'dynamic_resist':{'trend_stat':R_stat,'candle_stat':candle_R_stats},
                            # 'candle_location':{'support':candle_location['support'],'resist':candle_location['resist']},
                            'support_dynamic_trend_long':{'p0_x':p0_sup_long_x,'p0_y':p0_sup_long_y,'m':m_sup_long,'r2':r2_sup_long},
                            'resist_dynamic_trend_long':{'p0_x':p0_res_long_x,'p0_y':p0_res_long_y,'m':m_res_long,'r2':r2_res_long},
                            'dynamic_support_long':{'trend_stat':S_long_stat,'candle_stat':candle_S_long_stats},
                            'dynamic_resist_long':{'trend_stat':R_long_stat,'candle_stat':candle_R_long_stats},
                            'dynamic_last_pivots':last_pivots,
                            'candle_location_long':{'support':candle_location_long['support'],'resist':candle_location_long['resist']},
                            'sma_stat':sma_stat, 'ema_entry_signal':ema_entry_signal,'ema_exit_signal':ema_exit_signal, 
                            'rsi_data':rsi_data,'bollinger_data':bollinger_data,'ema_150_trend':ema_150_trend}
                del df
                del df_long
                del df_short
                del last_candles
                del rsi_xs
                del rsi_ys
                gc.collect()
                
    def calculate_situations(self):
        dict=self.dict
        for tf in dict:
            adj_th=self.adjust_threshold(tf)
            candle=dict[tf]['df_short'].iloc[-1]
            prelast_candle=dict[tf]['df_short'].iloc[-2]
            sit=s.Situation()
            sit.tf=tf
            sit.long_term_df=dict[tf]['df_long']
            sit.short_term_df=dict[tf]['df_short']
            sit.trend_break_level=dict[tf]['break_level']
            sit.candle_color=dict[tf]['last_candle_color']
            sit.ichi_stat=dict[tf]['ichi_stat']
            sit.ichi_bermuda=dict[tf]['ichi_bermuda']
            sit.long_trend_stat=dict[tf]['long_trend']
            sit.short_trend_stat=dict[tf]['short_trend']
            sit.current_trend_stat=dict[tf]['current_trend']
            sit.long_trend_points=dict[tf]['long_trend_points']
            sit.short_trend_points=dict[tf]['short_trend_points']

            # sit.dynamic_support_stats=dict[tf]['dynamic_support']['candle_stat']
            # sit.dynamic_support_line=dict[tf]['support_dynamic_trend']
            # sit.dynamic_resist_stats=dict[tf]['dynamic_resist']['candle_stat']
            # sit.dynamic_resist_line=dict[tf]['resist_dynamic_trend']
            # sit.dynamic_support_candle_location=dict[tf]['candle_location']['support']
            # sit.dynamic_resist_candle_location=dict[tf]['candle_location']['resist']

            sit.dynamic_support_long_stats=dict[tf]['dynamic_support_long']['candle_stat']
            sit.dynamic_support_long_line=dict[tf]['support_dynamic_trend_long']
            sit.dynamic_resist_long_stats=dict[tf]['dynamic_resist_long']['candle_stat']
            sit.dynamic_resist_long_line=dict[tf]['resist_dynamic_trend_long']
            sit.dynamic_support_long_candle_location=dict[tf]['candle_location_long']['support']
            sit.dynamic_resist_long_candle_location=dict[tf]['candle_location_long']['resist']
            sit.dynamic_last_pivots=dict[tf]['dynamic_last_pivots']
            sit.fibo_level_retrace_stat=dict[tf]['fibo']['retrace']['stat']
            sit.fibo_level_trend_stat=dict[tf]['fibo']['trend']['stat']
            sit.fibo_retrace_levels=dict[tf]['fibo']['retrace']['levels']
            sit.fibo_trend_levels=dict[tf]['fibo']['trend']['levels']
            sit.fibo_level_retrace_dir=dict[tf]['fibo']['retrace']['dir']
            sit.fibo_level_trend_dir=dict[tf]['fibo']['trend']['dir']            
            sit.static_levels=dict[tf]['static_levels']
            sit.last_candles_diection=dict[tf]['last_candles_diection']

            for j in range(0,len(sit.static_levels)):
                l=sit.static_levels[j]
                l0=()
                l1=()
                if j>0:l0=sit.static_levels[j-1]
                if j<len(sit.static_levels)-1:l1=sit.static_levels[j+1]
                candle_stats=helper.Candle_level_stat(l[1],l[0],candle,sit.last_candles_diection, threshold=adj_th)
                if len(candle_stats)>0:
                    sit.static_level_stats=candle_stats
                    prelast_candle_stats=helper.Candle_level_stat(l[1],l[0],prelast_candle,sit.last_candles_diection, threshold=adj_th)
                    if len(prelast_candle_stats)>0:
                        sit.prelast_candle_static_level_stats=prelast_candle_stats
                        sit.position_level_bot=l0
                        sit.position_level_middle=l
                        sit.position_level_top=l1
                    break


            tf_parent_index=self.tfs.index (tf)-1
            
            if tf_parent_index>=0:
                tf_p=self.tfs[tf_parent_index]
                sit.short_term_df_parent=dict[tf_p]['df_short']
                sit.long_term_df_parent=dict[tf_p]['df_long']
                sit.dynamic_support_line_parent=dict[tf_p]['support_dynamic_trend_long']
                sit.dynamic_resist_line_parent=dict[tf_p]['resist_dynamic_trend_long']
                sit.ichi_parent_stat=dict[tf_p]['ichi_stat']

                levels_parent=dict[tf_p]['static_levels']
                sit.parent_static_levels=levels_parent
                for l in levels_parent:
                    candle_stats=helper.Candle_level_stat(l[1],l[0],candle,sit.last_candles_diection,threshold=adj_th)
                    if len(candle_stats)>0:
                        sit.parent_level_stats=candle_stats
                        break
                for j in range(0,len(sit.parent_static_levels)):
                    l=sit.parent_static_levels[j]
                    l0=()
                    l1=()
                    if j>0:l0=sit.parent_static_levels[j-1]
                    if j<len(sit.parent_static_levels)-1:l1=sit.parent_static_levels[j+1]
                    candle_stats=helper.Candle_level_stat(l[1],l[0],candle,sit.last_candles_diection, threshold=adj_th)
                    if len(candle_stats)>0:
                        sit.parent_level_stats=candle_stats
                        prelast_candle_stats=helper.Candle_level_stat(l[1],l[0],prelast_candle,sit.last_candles_diection, threshold=adj_th)
                        if len(prelast_candle_stats)>0:
                            sit.parent_prelast_candle_static_level_stats=prelast_candle_stats
                            sit.parent_position_level_bot=l0
                            sit.parent_position_level_middle=l
                            sit.parent_position_level_top=l1
                        break                    
                pivots = pd.DataFrame(
                    data=dict[tf]['df_long'][np.logical_or(dict[tf]['df_long']["pivot"] == 1, dict[tf]['df_long']["pivot"] == 2)],
                    columns=["row_index", "low", "high", "pivot"],
                )
                last_pivot = pivots[-1:]

                remaining_candles=dict[tf]['df_long'][-len(dict[tf_p]['df_long'])+last_pivot.index.values[0]+1:-1].reset_index(drop=True)              
                 #sit.parent_dynamic_support_stats,sit.parent_dynamic_resist_stats,candle_location=helper.Candle_Dynamic_Trend_Stat(candle=candle,supp_data=dict[tf_p]['support_dynamic_trend'],res_data=dict[tf_p]['resist_dynamic_trend'],r_min=0.95,last_candles_diection=sit.last_candles_diection, threshold=adj_th)
                _,sit.parent_dynamic_support_stats,_,sit.parent_dynamic_resist_stats,candle_location=helper.Dynamic_SR(df=dict[tf_p]['df_long'],remaining_candles=remaining_candles,candle=candle, threshold=adj_th,n=self.pvt_trend_number)
                sit.dynamic_resist_candle_location_parent=candle_location["resist"]
                sit.dynamic_support_candle_location_parent=candle_location["support"]

                sit.fibo_parent_level_retrace_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['retrace']['levels'],tf=tf_p,thb=adj_th)
                sit.fibo_parent_level_retrace_dir=dict[tf_p]['fibo']['retrace']['dir']
                sit.fibo_parent_retrace_levels=dict[tf_p]['fibo']['retrace']['levels']
                sit.fibo_parent_level_trend_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['trend']['levels'],tf=tf_p, thb=adj_th)
                sit.fibo_parent_level_trend_dir=dict[tf_p]['fibo']['trend']['dir']
                sit.fibo_parent_trend_levels=dict[tf_p]['fibo']['trend']['levels']
                
            sit.candle_shapes=helper.Candle_Shapes(candle=candle,th=adj_th)
            sit.double_bot_happened=dict[tf]['double_bot_level'] 
            sit.double_top_happened=dict[tf]['double_top_level'] 

            sit.sma_10_50_cross_up_happened=dict[tf]['sma_stat']
            sit.ema_5_10_30_buy_signal=dict[tf]['ema_entry_signal']
            sit.ema_5_10_30_sell_signal=dict[tf]['ema_exit_signal']
            sit.rsi_divergance=dict[tf]['rsi_data']['dvg']
            sit.rsi_line=dict[tf]['rsi_data']['rsi_line']
            sit.rsi_chart_line=dict[tf]['rsi_data']['chart_line']
            sit.rsi_over_75=dict[tf]['rsi_data']['over_75']
            sit.rsi_below_30=dict[tf]['rsi_data']['below_30']
            sit.rsi=dict[tf]['rsi_data']['rsi']
            sit.bollinger_top_candle_location=dict[tf]['bollinger_data']['upper']
            sit.bollinger_bot_candle_location=dict[tf]['bollinger_data']['lower']
            sit.ema_150_trend=dict[tf]['ema_150_trend']
            self.situations[tf]=sit
        del dict
        gc.collect()
   
    def report_buy_00(self,tf):
        dict_buy_sell=self.situations[tf].buy_sell_v01()
        sit_tf_buy=self.situations[tf].buy_position_01()
        total_points=round(sit_tf_buy[1]-sit_tf_buy[3],2)
        header=f'{tf} point: {total_points}'
        opp_points=f"Opportunities with point: {sit_tf_buy[1]}"
        opp=sit_tf_buy[0]
        threat_point=f"Threats with point: {sit_tf_buy[3]}"
        threat=sit_tf_buy[2]
        return header,opp_points,opp,threat_point,threat,total_points
    def buy_sell(self,tf):
        return self.situations[tf].buy_sell_v01()
    def features(self,tf):
        return self.situations[tf].features()
    def level_bounce_position(self,tf):
        return self.situations[tf].level_bounce_position()
    def fibo_position(self,tf):
        return self.situations[tf].fibo_position()
    def dynamic_SR_position(self,tf):
        return self.situations[tf].dynamic_SR_position()
