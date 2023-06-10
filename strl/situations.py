import Constants as c
class Parametrs:
    def __init__(self):
        self.price_action_trend=[1,False]
        self.price_action_trend_parent=[0.6,False]
        self.price_action_trend_grand_parent=[0.2,False]
        self.channel_break=[0.8,False]
        self.channel_boundries=[0.7,False]
        self.triangle_break=[0.8,False]
        self.double_hits=[0.8,False]
        self.rsi_divergence=[0.7,False]
        self.fibo_retrace=[0.6,False]
        self.fibo_retrace_parent=[0.2,False]
        self.ichi_location=[0.6,False]
        self.ichi_location_parent=[0.2,False]
        self.dynamic_SR_closeness=[1.5,False] #Short Term Dynamic S/R
        self.dynamic_SR_long_closeness=[1,False]
        self.dynamic_SR_closeness_parrent=[0.5,False]
        self.static_SR_closeness=[1.5,False]
        self.static_SR_closeness_parent=[0.5,False]    
        self.sma_50_10=[0.5,False]
    
    def calc_points(self):
        all=[
                self.price_action_trend,
                self.price_action_trend_parent,
                self.price_action_trend_grand_parent,
                self.channel_break,
                self.channel_boundries,
                self.triangle_break,
                self.double_hits,
                self.rsi_divergence,
                self.fibo_retrace,
                self.fibo_retrace_parent,
                self.ichi_location,
                self.ichi_location_parent,
                self.dynamic_SR_closeness,
                self.dynamic_SR_long_closeness,
                self.dynamic_SR_closeness_parrent,
                self.static_SR_closeness,
                self.static_SR_closeness_parent,
                self.sma_50_10
            ]
        return sum(a[0]*a[1] for a in all) 
class Situation:
    def __init__(self):
        self.tf='1d'
        self.short_term_df_parent=None
        self.short_term_df=None
        self.short_trend_points=[]
        self.long_term_df=None
        self.long_trend_points=[]
        self.trend_break_level=0
        self.candle_color=c.Candle_Color.Green
        self.candle_shapes=[]
        self.current_trend_stat=c.Trend.Nothing
        self.long_trend_stat=c.Trend.Nothing
        self.short_trend_stat=c.Trend.Nothing
        

        self.dynamic_support_stats=[]
        self.dynamic_support_line={}
        self.dynamic_resist_stats=[]
        self.dynamic_resist_line={}
        self.dynamic_support_long_stats=[]
        self.dynamic_support_long_line={}
        self.dynamic_resist_long_stats=[]
        self.dynamic_resist_long_line={}

        self.parent_dynamic_support_stats=[]
        self.dynamic_support_line_parent={}
        self.parent_dynamic_resist_stats=[]
        self.dynamic_resist_line_parent={}

        self.ichi_stat=c.Ichi_Stat.Nothing
        self.ichi_parent_stat=c.Ichi_Stat.Nothing

        # self.sma_50_stat=c.SMA_Stat.Above
        # self.sma_21_stat=c.SMA_Stat.Above
        # self.sma_10_stat=c.SMA_Stat.Above

        self.static_level_stats=[]
        self.parent_level_stats=[]
        self.static_levels=[]
        self.parent_static_levels=[]
        self.last_candles_diection=c.Candles_Direction.Side
        self.fibo_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_level_trend_dir=c.Fibo_Direction.Up
        self.fibo_retrace_levels=[]
        self.fibo_trend_levels=[]


        self.fibo_parent_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_parent_level_trend_dir=c.Fibo_Direction.Up
        self.fibo_parent_retrace_levels=[]
        self.fibo_parent_trend_levels=[]

        self.fibo_grand_parent_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_grand_parent_level_trend_dir=c.Fibo_Direction.Up
        self.fibo_grand_parent_retrace_levels=[]
        self.fibo_grand_parent_trend_levels=[]


        self.double_top_happened=0
        self.double_bot_happened=0

        self.sma_10_50_cross_up_happened=False

        self.rsi_divergance=c.Rsi_Stat.Nothing
        self.rsi_chart_line=[]
        self.rsi_line=[]

        
    def break_important_level_up(self):
        return self.parent_level_stat==c.Candle_Level_Area_Stat.Broke_Resist
    def break_important_level_down(self):
        return self.parent_level_stat==c.Candle_Level_Area_Stat.Broke_Support

    def buy_position_01(self):
        threat_bearish=False
        threat_triangle=False
        threat_double_top=False
        threat_rsi_divergence=False
        threat_grand_parent_retrace=False
        threat_ichi_below_green=False
        threat_near_resistance=False


        bullish_trend=False
        candle_above_dynamic_support=False
        candle_above_parent_dynamic_support=False
        candle_above_parent_static_level=False
        candle_above_static_Level=False
        candle_ichi_above=False
        parent_ichi_above=False
        double_bot_momentum=False
        triangle_momentum=False
        sma_50_10=False

        if self.current_trend_stat==c.Trend.Bullish:
            bullish_trend=True
        if self.dynamic_support_stat==c.Candle_Dynamic_SR_Stat.Low_Above_Support and self.candle_shapes.__contains__(c.Candle_Shape.Small):
            candle_above_dynamic_support=True
        if self.parent_dynamic_support_stat==c.Candle_Dynamic_SR_Stat.Low_Above_Support and self.candle_shapes.__contains__(c.Candle_Shape.Small):
            candle_above_parent_dynamic_support=True

        if self.parent_level_stat==c.Candle_Level_Area_Stat.Near_Support or self.parent_level_stat==c.Candle_Level_Area_Stat.Closed_In_Support:
            candle_above_parent_static_level=True
        if self.static_level_stat==c.Candle_Level_Area_Stat.Near_Support or self.static_level_stat==c.Candle_Level_Area_Stat.Closed_In_Support:
            candle_above_static_Level=True

        if self.ichi_stat==c.Ichi_Stat.Above_Green or self.ichi_stat==c.Ichi_Stat.Above_Red:
            candle_ichi_above=True
        if self.ichi_parent_stat==c.Ichi_Stat.Above_Green or self.ichi_parent_stat==c.Ichi_Stat.Above_Red:
            parent_ichi_above=True
        double_bot_momentum=self.double_bot_happened !=0
        sma_50_10=self.sma_10_50_cross_up_happened
        
        
        if self.current_trend_stat==c.Trend.Bearish:
            threat_bearish=True

        if self.fibo_grand_parent_level_trend_stat !=c.Candle_Fibo_Stat.Nothing:
            threat_grand_parent_retrace=True
        if self.ichi_stat==c.Ichi_Stat.Below_Green :
            threat_ichi_below_green=True

        threat_double_top=self.double_top_happened !=0

        threats=[(threat_bearish,1),(threat_triangle,1),(threat_double_top,1),
                 (threat_rsi_divergence,1),(threat_grand_parent_retrace,1),(threat_ichi_below_green,0.3)]
        opportunities=[(bullish_trend,1),(triangle_momentum,1),(double_bot_momentum,1),
                       (candle_above_dynamic_support or candle_above_parent_dynamic_support,2),
                       (candle_above_parent_static_level,0.5),(candle_above_static_Level,0.5),(sma_50_10,0.5),
                       (candle_ichi_above,0.3),(parent_ichi_above,0.2)]

        
        opp_points= sum(o[0]*o[1] for o in opportunities)          
        threat_points= sum(t[0]*t[1] for t in threats)  

        dict_opp={'Bullish Trend':bullish_trend,'Triangle Momentum':triangle_momentum,'Double Bot Momentum':double_bot_momentum,
              'Near Support':candle_above_dynamic_support or candle_above_parent_dynamic_support,
              'Candle Above Parent Static Level':candle_above_parent_static_level,'Candle Above Static Level':candle_above_static_Level,
              'Above Ichi':candle_ichi_above,'Parent Above Ichi':parent_ichi_above}
        
        dict_threats={'Bearish Trend':threat_bearish,'Triangle Break Down':threat_triangle,'Double Top Resistance':threat_double_top,
        'Grand Parent Retracement':threat_grand_parent_retrace,'Ichi Below Green':threat_ichi_below_green}



        return dict_opp,opp_points,dict_threats,threat_points

    def buy_sell_v01(self):

        buy_pars=Parametrs()
        sell_pars=Parametrs()
        
##      Trend Status

        if self.current_trend_stat==c.Trend.Bullish:
            buy_pars.price_action_trend[1]=True
        if self.current_trend_stat==c.Trend.Bearish:
            sell_pars.price_action_trend[1]=True

##      Dynamic Support/Resistance Closeness
        
        dcst=c.Candle_Dynamic_SR_Stat
        dynamic_support_rules=[dcst.Close_Near_Support,dcst.Open_Near_Support,dcst.Shadow_Near_Support]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.dynamic_support_stats for i in dynamic_support_rules):
            buy_pars.dynamic_SR_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.dynamic_support_long_stats for i in dynamic_support_rules):
            buy_pars.dynamic_SR_long_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.parent_dynamic_support_stats for i in dynamic_support_rules):
            buy_pars.dynamic_SR_closeness_parrent[1]=True

        dynamic_resist_rules=[dcst.Close_Near_Resist,dcst.Open_Near_Resist,dcst.Shadow_Near_Resist]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.dynamic_resist_stats for i in dynamic_resist_rules):
            sell_pars.dynamic_SR_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.dynamic_resist_long_stats for i in dynamic_resist_rules):
            sell_pars.dynamic_SR_long_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.parent_dynamic_resist_stats for i in dynamic_resist_rules):
            sell_pars.dynamic_SR_closeness_parrent[1]=True


##      Static Support/Resistance Closeness

        cst=c.Candle_Level_Area_Stat
        static_support_rules=[cst.Closed_Near_Support,cst.Closed_In_Support,cst.Shadow_In_Support,cst.Shadow_Near_Support,cst.Opened_In_Support,cst.Opened_Near_Support]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.static_level_stats for i in static_support_rules):
            buy_pars.static_SR_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.parent_level_stats for i in static_support_rules):
            buy_pars.static_SR_closeness_parent[1]=True

        static_resist_rules=[cst.Closed_Near_Resist,cst.Closed_In_Resist,cst.Shadow_In_Resist,cst.Shadow_Near_Resist,cst.Opened_In_Resist,cst.Opened_Near_Resist]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.static_level_stats for i in static_resist_rules):
            sell_pars.static_SR_closeness[1]=True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(i in self.parent_level_stats for i in static_resist_rules):
            sell_pars.static_SR_closeness_parent[1]=True

##      Ichi Status

        if self.ichi_stat==c.Ichi_Stat.Above_Green :
            buy_pars.ichi_location[1]=True
        if self.ichi_parent_stat==c.Ichi_Stat.Above_Green :
            buy_pars.ichi_location_parent[1]=True
        if self.ichi_stat==c.Ichi_Stat.Below_Green :
            sell_pars.ichi_location[1]=True
        if self.ichi_parent_stat==c.Ichi_Stat.Below_Green :
            sell_pars.ichi_location_parent[1]=True

 ##     Double Bot/Top Status
        
        if self.double_bot_happened !=0:
            buy_pars.double_hits[1]=True
        if self.double_top_happened !=0:
            sell_pars.double_hits[1]=True

##      SMA 10 / 50 Status

        if self.sma_10_50_cross_up_happened:
            buy_pars.sma_50_10[1]=True
        if not self.sma_10_50_cross_up_happened:
            sell_pars.sma_50_10[1]=True        

##      RSI Divergence
        if self.rsi_divergance==c.Rsi_Stat.Up:
            buy_pars.rsi_divergence[1]=True
        if self.rsi_divergance==c.Rsi_Stat.Down:
            sell_pars.rsi_divergence[1]=True

        return {"buy":buy_pars,"sell":sell_pars}





