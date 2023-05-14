
import helper
import Constants as c
import pivot_helper
import situations as s
class Analyzer:
    def __init__(self):
        self.tfs=['1d', '4h', '1h', '15m']
        self.trend_limit_long=280
        self.trend_limit_short=80
        self.long_term_pivot_candles=16
        self.short_term_pivot_candles=6
        self.waves_number=2
        self.pvt_trend_number=2
        self.analysis='1.0'
        self.symbol='BTC_USDT'
        self.exch='Kucoin'
        self.dict={}
        self.situations={}
        self.threshold=0.005

    def init_data(self,tfs=['1d', '4h', '1h', '15m'],trend_limit_long=280,trend_limit_short=80,long_term_pivot_candles=16,short_term_pivot_candles=6,waves_number=2,pvt_trend_number=2,
             analysis='1.0',symbol='BTC_USDT',exch='Kucoin',candles_back=0,th=0.005):
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
    
    def calculate_dict(self,candles_back=0):
        if self.analysis == '1.0':
            for tf in self.tfs:
                df = helper.GetData(tf, self.symbol, self.exch)
                df_long = df[len(df)-self.trend_limit_long-candles_back:len(df)-candles_back].reset_index(drop=True)
                df_short = df[len(df)-self.trend_limit_short-candles_back:len(df)-candles_back].reset_index(drop=True)
                df_long = pivot_helper.find_pivots(
                    df_long, self.long_term_pivot_candles, self.long_term_pivot_candles, self.waves_number, short=True)
                df_short = pivot_helper.find_pivots(
                    df_short, self.short_term_pivot_candles, self.short_term_pivot_candles, 2, short=True)

                trend_long,long_up_points,long_down_points = helper.TrendDirection(df_long)
                trend_short,short_up_points,short_down_points = helper.TrendDirection(df_short)
                pa_break, is_break,break_level = helper.PA_Break(
                    df_long, trend_long, trend_short)

                static_levels = helper.GetImportantLevels(
                    df_short, threshold=self.threshold*2, combined=True)

                helper.append_ichi(df_short)
                ichi_status = helper.GetIchiStatus(df_short)
                db_bot, db_top = helper.double_levels(df_long, threshold=self.threshold)

                current_trend=c.Trend.Nothing
                if trend_long == c.Trend.Bullish:
                    if (trend_short == c.Trend.Bearish and is_break):
                        current_trend=c.Trend.Bearish
                    elif (trend_short == c.Trend.Bearish and not is_break) or (trend_short==c.Trend.Bullish):
                        current_trend=c.Trend.Bullish
                elif trend_long == c.Trend.Bearish:
                    if (trend_short == c.Trend.Bullish and is_break):
                        current_trend=c.Trend.Bullish
                    elif (trend_short == c.Trend.Bullish and not is_break) or (trend_short == c.Trend.Bearish):
                        current_trend=c.Trend.Bearish

                last_candles=df_short[-self.short_term_pivot_candles:].reset_index(drop=True)
                last_candles_diection=helper.Candles_direction(last_candles)
                S_stat,candle_S_stats,R_stat,candle_R_stats=helper.Dynamic_SR(df=df_short,last_candles_diection=last_candles_diection,threshold=self.threshold,n=self.pvt_trend_number)
                p0_sup_x,p0_sup_y,m_sup,r2_sup=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=self.pvt_trend_number,mode=1)
                p0_res_x,p0_res_y,m_res,r2_res=helper.Return_Trend_From_DF(df_short,r_min=0.95,n=self.pvt_trend_number,mode=2)

                fibo_dir_retrace,fibo_stat_retrace,fibo_retrace_levels=helper.FiboStat(df=df_short,fibomode=c.Fibo_Mode.Retracement,threshold=self.threshold)
                fibo_dir_trend,fibo_stat_trend,fibo_trend_levels=helper.FiboStat(df=df_long,fibomode=c.Fibo_Mode.Trend_Base_Extension,threshold=self.threshold)
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
                            'pa_break': pa_break, 'is_break': is_break, 'break_level':break_level,
                            'static_levels': static_levels,
                            'support_dynamic_trend':{'p0_x':p0_sup_x,'p0_y':p0_sup_y,'m':m_sup,'r2':r2_sup},
                            'resist_dynamic_trend':{'p0_x':p0_res_x,'p0_y':p0_res_y,'m':m_res,'r2':r2_res},
                            'ichi_stat': ichi_status, 'double_bot_level': db_bot,'double_top_level': db_top,
                            'fibo':{'retrace':fibo_data_retrace,'trend':fibo_data_trend},
                            'dynamic_support':{'trend_stat':S_stat,'candle_stat':candle_S_stats},
                            'dynamic_resist':{'trend_stat':R_stat,'candle_stat':candle_R_stats}}
    def calculate_situations(self):
        dict=self.dict
        for tf in dict:
            candle=dict[tf]['df_short'].iloc[-1]
            sit=s.Situation()
            sit.tf=tf
            sit.long_term_df=dict[tf]['df_long']
            sit.short_term_df=dict[tf]['df_short']
            sit.trend_break_level=dict[tf]['break_level']
            sit.candle_color=dict[tf]['last_candle_color']
            sit.ichi_stat=dict[tf]['ichi_stat']
            sit.long_trend_stat=dict[tf]['long_trend']
            sit.short_trend_stat=dict[tf]['short_trend']
            sit.current_trend_stat=dict[tf]['current_trend']
            sit.long_trend_points=dict[tf]['long_trend_points']
            sit.short_trend_points=dict[tf]['short_trend_points']
            sit.dynamic_support_stats=dict[tf]['dynamic_support']['candle_stat']
            sit.dynamic_support_line=dict[tf]['support_dynamic_trend']
            sit.dynamic_resist_stats=dict[tf]['dynamic_resist']['candle_stat']
            sit.dynamic_resist_line=dict[tf]['resist_dynamic_trend']
            sit.fibo_level_retrace_stat=dict[tf]['fibo']['retrace']['stat']
            sit.fibo_level_trend_stat=dict[tf]['fibo']['trend']['stat']
            sit.fibo_retrace_levels=dict[tf]['fibo']['retrace']['levels']
            sit.fibo_trend_levels=dict[tf]['fibo']['trend']['levels']
            sit.static_levels=dict[tf]['static_levels']
            sit.last_candles_diection=dict[tf]['last_candles_diection']
            for l in sit.static_levels:
                candle_stats=helper.Candle_level_stat(l[1],l[0],candle,sit.last_candles_diection, threshold=self.threshold)
                if len(candle_stats)>0:
                    sit.static_level_stats=candle_stats
                    break


            tf_parent_index=self.tfs.index (tf)-1
            
            if tf_parent_index>=0:
                tf_p=self.tfs[tf_parent_index]
                sit.short_term_df_parent=dict[tf_p]['df_short']
                sit.dynamic_support_line_parent=dict[tf_p]['support_dynamic_trend']
                sit.dynamic_resist_line_parent=dict[tf_p]['resist_dynamic_trend']
                sit.ichi_parent_stat=dict[tf_p]['ichi_stat']

                levels_parent=dict[tf_p]['static_levels']
                sit.parent_static_levels=levels_parent
                for l in levels_parent:
                    candle_stats=helper.Candle_level_stat(l[1],l[0],candle,sit.last_candles_diection,threshold=self.threshold)
                    if len(candle_stats)>0:
                        sit.parent_level_stats=candle_stats
                        break
                sit.parent_dynamic_support_stats,sit.parent_dynamic_resist_stats=helper.Candle_Dynamic_Trend_Stat(candle=candle,supp_data=dict[tf_p]['support_dynamic_trend'],res_data=dict[tf_p]['resist_dynamic_trend'],r_min=0.95,last_candles_diection=sit.last_candles_diection, threshold=self.threshold)

                sit.fibo_parent_level_retrace_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['retrace']['levels'],tf=tf_p,thb=self.threshold)
                sit.fibo_parent_level_retrace_dir=dict[tf_p]['fibo']['retrace']['dir']
                sit.fibo_parent_retrace_levels=dict[tf_p]['fibo']['retrace']['levels']
                sit.fibo_parent_level_trend_stat=helper.Candle_fibo_levle_stat(candle=candle,levels=dict[tf_p]['fibo']['trend']['levels'],tf=tf_p, thb=self.threshold)
                sit.fibo_parent_level_trend_dir=dict[tf_p]['fibo']['trend']['dir']
                sit.fibo_parent_trend_levels=dict[tf_p]['fibo']['trend']['levels']
                
            sit.candle_shapes=helper.Candle_Shapes(candle=candle,th=self.threshold)
            sit.double_bot_happened=dict[tf]['double_bot_level'] 
            sit.double_top_happened=dict[tf]['double_top_level'] 

            self.situations[tf]=sit
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

