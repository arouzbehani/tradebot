import Constants as c
class Situation:
    def __init__(self):
        self.tf='1d'
        self.candle_color=c.Candle_Color.Green
        self.candle_shapes=[]
        self.current_trend_stat=c.Trend.Nothing
        self.long_trend_stat=c.Trend.Nothing
        self.short_trend_stat=c.Trend.Nothing

        self.dynamic_support_stat=c.Candle_Dynamic_SR_Stat.Nothing
        self.dynamic_resist_stat=c.Candle_Dynamic_SR_Stat.Nothing
        self.parent_dynamic_support_stat=c.Candle_Dynamic_SR_Stat.Nothing
        self.parent_dynamic_resist_stat=c.Candle_Dynamic_SR_Stat.Nothing

        self.ichi_stat=c.Ichi_Stat.Nothing
        self.ichi_parent_stat=c.Ichi_Stat.Nothing

        self.sma_50_stat=c.SMA_Stat.Above
        self.sma_21_stat=c.SMA_Stat.Above
        self.sma_10_stat=c.SMA_Stat.Above

        self.parent_level_stat=c.Candle_Level_Area_Stat.Nothing

        self.fibo_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_level_trend_dir=c.Fibo_Direction.Up

        self.fibo_parent_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_parent_level_trend_dir=c.Fibo_Direction.Up

        self.fibo_grand_parent_level_retrace_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_trend_stat=c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_retrace_dir=c.Fibo_Direction.Up
        self.fibo_grand_parent_level_trend_dir=c.Fibo_Direction.Up
        self.double_top_happened=0
        self.double_bot_happened=0

        self.sma_10_50_cross_up_happened=False
        self.sma_10_50_cross_down_happened=False

        self.rsi_convergence_up=False
        self.rsi_convergence_down=False
        self.rsi_below_35_happened=False
        self.rsi_above_65_happened=False
    
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


        bullish_trend=False
        candle_above_dynamic_support=False
        candle_above_parent_dynamic_support=False
        candle_above_parent_level=False
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
            candle_above_parent_level=True
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
                       (candle_above_dynamic_support or candle_above_parent_dynamic_support,1),
                       (candle_above_parent_level,0.5),(sma_50_10,0.5),
                       (candle_ichi_above,0.3),(parent_ichi_above,0.2)]

        
        opp_points= sum(o[0]*o[1] for o in opportunities)          
        threat_points= sum(t[0]*t[1] for t in threats)  

        dict_opp={'Bullish Trend':bullish_trend,'Triangle Momentum':triangle_momentum,'Double Bot Momentum':double_bot_momentum,
              'Near Support':candle_above_dynamic_support or candle_above_parent_dynamic_support,
              'Candle Above Parent Level':candle_above_parent_level,'Above Ichi':candle_ichi_above,'Parent Above Ichi':parent_ichi_above}
        
        dict_threats={'Bearish Trend':threat_bearish,'Triangle Break Down':threat_triangle,'Double Top Resistance':threat_double_top,
        'Grand Parent Retracement':threat_grand_parent_retrace,'Ichi Below Green':threat_ichi_below_green}



        return dict_opp,opp_points,dict_threats,threat_points






