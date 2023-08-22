import Constants as c, analaysis_constants as ac
import talib, patterns


class Parametrs:
    def __init__(self):
        self.ema_150_trend = [1, False]
        self.price_action_trend = [1, False]
        self.price_action_trend_parent = [0.5, False]
        self.price_action_trend_grand_parent = [0.3, False]
        self.channel_break = [1, False]
        self.channel_boundries = [1, False]
        self.triangle_break = [1, False]
        self.double_hits = [1, False]
        self.rsi_divergence = [0.7, False]
        self.rsi_cross_limits = [0.2, False]
        self.fibo_retrace = [1, False]
        self.fibo_retrace_parent = [0.5, False]
        self.fibo_trend = [1, False]
        self.fibo_trend_parent = [0.5, False]
        self.ichi_location = [0.5, False]
        self.ichi_location_parent = [0.3, False]
        # self.dynamic_SR_closeness = [1.5, False]  # Short Term Dynamic S/R
        self.dynamic_SR_long_closeness = [1, False]
        self.dynamic_SR_closeness_parrent = [0.5, False]
        self.static_SR_closeness = [1, False]
        self.static_SR_closeness_parent = [0.5, False]
        self.ema_5_10_30 = [0.5, False]
    def calc_array_points(self,all):
        return sum(a[0] * a[1] for a in all)
    def calc_points(self):

        all = [
            self.price_action_trend,
            self.price_action_trend_parent,
            self.price_action_trend_grand_parent,
            self.channel_break,
            self.channel_boundries,
            self.triangle_break,
            self.double_hits,
            self.rsi_divergence,
            self.rsi_cross_limits,
            self.fibo_retrace,
            self.fibo_retrace_parent,
            self.fibo_trend,
            self.fibo_trend_parent,
            self.ichi_location,
            self.ichi_location_parent,
            #self.dynamic_SR_closeness,
            self.dynamic_SR_long_closeness,
            self.dynamic_SR_closeness_parrent,
            self.static_SR_closeness,
            self.static_SR_closeness_parent,
            # self.sma_50_10,
            self.ema_5_10_30,
            self.ema_150_trend,
        ]
        return sum(a[0] * a[1] for a in all)

    def calc_pars(self):
        calcpars = {
            "trend_pars": [
                self.price_action_trend,
                self.price_action_trend_parent,
                self.price_action_trend_grand_parent,
                self.ema_150_trend,
            ],
            "current_static_level_pars": [self.static_SR_closeness],
            "parent_static_level_pars": [self.static_SR_closeness_parent],
            # "dynamic_SR_pars": [self.dynamic_SR_closeness],
            "dynamic_SR_pars_long": [
                self.dynamic_SR_long_closeness,
            ],
            "dynamic_SR_pars_parent": [
                self.dynamic_SR_closeness_parrent,
            ],
            # "sma_10_50_pars": [self.sma_50_10],
            "ema_5_10_30": [
                self.ema_5_10_30,
            ],
            "ichi_stat_pars": [
                self.ichi_location,
            ],
            "ichi_stat_pars_parent": [
                self.ichi_location_parent,
            ],
            "rsi_dicergence_pars": [
                self.rsi_divergence,
            ],
            "fibo_retreace_pars": [
                self.fibo_retrace,
            ],
            "fibo_trend_pars": [
                self.fibo_trend,
            ],
        }
        return calcpars

class Situation:
    def __init__(self):
        self.tf = "1d"
        self.short_term_df_parent = None
        self.short_term_df = None
        self.short_trend_points = []
        self.long_term_df = None
        self.long_trend_points = []
        self.trend_break_level = 0
        self.candle_color = c.Candle_Color.Green
        self.candle_shapes = []
        self.current_trend_stat = c.Trend.Nothing
        self.long_trend_stat = c.Trend.Nothing
        self.short_trend_stat = c.Trend.Nothing
        self.ema_150_trend = c.Trend.Nothing

        # self.dynamic_support_stats = []
        # self.dynamic_support_line = {}
        # self.dynamic_support_candle_location = {}
        # self.dynamic_resist_stats = []
        # self.dynamic_resist_line = {}
        # self.dynamic_resist_candle_location = {}
        self.dynamic_last_pivots=[]
        self.dynamic_support_long_stats = []
        self.dynamic_support_long_line = {}
        self.dynamic_support_long_candle_location = {}
        self.dynamic_resist_long_stats = []
        self.dynamic_resist_long_line = {}
        self.dynamic_resist_long_candle_location = {}

        self.parent_dynamic_support_stats = []
        self.dynamic_support_line_parent = {}
        self.dynamic_support_candle_location_parent = {}
        self.parent_dynamic_resist_stats = []
        self.dynamic_resist_line_parent = {}
        self.dynamic_resist_candle_location_parent = {}

        self.ichi_stat = c.Ichi_Stat.Nothing
        self.ichi_parent_stat = c.Ichi_Stat.Nothing

        self.bollinger_top_candle_location = {}
        self.bollinger_bot_candle_location = {}
        # self.sma_50_stat=c.SMA_Stat.Above
        # self.sma_21_stat=c.SMA_Stat.Above
        # self.sma_10_stat=c.SMA_Stat.Above

        self.static_level_stats = []
        self.parent_level_stats = []

        self.prelast_candle_static_level_stats = []
        self.parent_prelast_candle_static_level_stats = []
        self.position_level_top = ()
        self.position_level_middle = ()
        self.position_level_bot = ()
        self.parent_position_level_top = ()
        self.parent_position_level_middle = ()
        self.parent_position_level_bot = ()
        self.static_levels = []
        self.parent_static_levels = []

        self.static_support_candle_location = {}
        self.static_resist_candle_location = {}

        self.static_support_candle_location_parent = {}
        self.static_resist_candle_location_parent = {}

        self.last_candles_diection = c.Candles_Direction.Side
        self.fibo_level_retrace_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_level_trend_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_level_retrace_dir = c.Fibo_Direction.Up
        self.fibo_level_trend_dir = c.Fibo_Direction.Up
        self.fibo_retrace_levels = []
        self.fibo_trend_levels = []

        self.fibo_parent_level_retrace_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_trend_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_parent_level_retrace_dir = c.Fibo_Direction.Up
        self.fibo_parent_level_trend_dir = c.Fibo_Direction.Up
        self.fibo_parent_retrace_levels = []
        self.fibo_parent_trend_levels = []

        self.fibo_grand_parent_level_retrace_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_trend_stat = c.Candle_Fibo_Stat.Nothing
        self.fibo_grand_parent_level_retrace_dir = c.Fibo_Direction.Up
        self.fibo_grand_parent_level_trend_dir = c.Fibo_Direction.Up
        self.fibo_grand_parent_retrace_levels = []
        self.fibo_grand_parent_trend_levels = []

        self.double_top_happened = 0
        self.double_bot_happened = 0

        self.sma_10_50_cross_up_happened = False
        self.ema_5_10_30_buy_signal = False
        self.ema_5_10_30_sell_signal = False
        self.rsi_divergance = c.Rsi_Stat.Nothing
        self.rsi_chart_line = []
        self.rsi_line = []
        self.rsi_over_75 = False
        self.rsi_below_30 = False
        self.rsi = -1

        self.bullish_reversal_patterns = [
            "CDLDOJI",
            "CDLENGULFING",
            "CDLHAMMER",
            "CDLINVERTEDHAMMER",
            "CDLHARAMI",
            "CDLMORNINGSTAR",
            "CDL3WHITESOLDIERS",
        ]
        self.bearish_reversal_patterns = [
            "CDLDOJI",
            "CDLENGULFING",
            "CDLHANGINGMAN",
            "CDLSHOOTINGSTAR",
            "CDLHARAMI",
            "CDLEVENINGSTAR",
            "CDL3BLACKCROWS",
        ]

    def break_important_level_up(self):
        return self.parent_level_stat == c.Candle_Level_Area_Stat.Broke_Resist

    def break_important_level_down(self):
        return self.parent_level_stat == c.Candle_Level_Area_Stat.Broke_Support

    def buy_position_01(self):
        threat_bearish = False
        threat_triangle = False
        threat_double_top = False
        threat_rsi_divergence = False
        threat_grand_parent_retrace = False
        threat_ichi_below_green = False
        threat_near_resistance = False

        bullish_trend = False
        candle_above_dynamic_support = False
        candle_above_parent_dynamic_support = False
        candle_above_parent_static_level = False
        candle_above_static_Level = False
        candle_ichi_above = False
        parent_ichi_above = False
        double_bot_momentum = False
        triangle_momentum = False
        sma_50_10 = False

        if self.current_trend_stat == c.Trend.Bullish:
            bullish_trend = True
        if (
            self.dynamic_support_stat == c.Candle_Dynamic_SR_Stat.Low_Above_Support
            and self.candle_shapes.__contains__(c.Candle_Shape.Small)
        ):
            candle_above_dynamic_support = True
        if (
            self.parent_dynamic_support_stat
            == c.Candle_Dynamic_SR_Stat.Low_Above_Support
            and self.candle_shapes.__contains__(c.Candle_Shape.Small)
        ):
            candle_above_parent_dynamic_support = True

        if (
            self.parent_level_stat == c.Candle_Level_Area_Stat.Near_Support
            or self.parent_level_stat == c.Candle_Level_Area_Stat.Closed_In_Support
        ):
            candle_above_parent_static_level = True
        if (
            self.static_level_stat == c.Candle_Level_Area_Stat.Near_Support
            or self.static_level_stat == c.Candle_Level_Area_Stat.Closed_In_Support
        ):
            candle_above_static_Level = True

        if (
            self.ichi_stat == c.Ichi_Stat.Above_Green
            or self.ichi_stat == c.Ichi_Stat.Above_Red
        ):
            candle_ichi_above = True
        if (
            self.ichi_parent_stat == c.Ichi_Stat.Above_Green
            or self.ichi_parent_stat == c.Ichi_Stat.Above_Red
        ):
            parent_ichi_above = True
        double_bot_momentum = self.double_bot_happened != 0
        sma_50_10 = self.sma_10_50_cross_up_happened

        if self.current_trend_stat == c.Trend.Bearish:
            threat_bearish = True

        if self.fibo_grand_parent_level_trend_stat != c.Candle_Fibo_Stat.Nothing:
            threat_grand_parent_retrace = True
        if self.ichi_stat == c.Ichi_Stat.Below_Green:
            threat_ichi_below_green = True

        threat_double_top = self.double_top_happened != 0

        threats = [
            (threat_bearish, 1),
            (threat_triangle, 1),
            (threat_double_top, 1),
            (threat_rsi_divergence, 1),
            (threat_grand_parent_retrace, 1),
            (threat_ichi_below_green, 0.3),
        ]
        opportunities = [
            (bullish_trend, 1),
            (triangle_momentum, 1),
            (double_bot_momentum, 1),
            (candle_above_dynamic_support or candle_above_parent_dynamic_support, 2),
            (candle_above_parent_static_level, 0.5),
            (candle_above_static_Level, 0.5),
            (sma_50_10, 0.5),
            (candle_ichi_above, 0.3),
            (parent_ichi_above, 0.2),
        ]

        opp_points = sum(o[0] * o[1] for o in opportunities)
        threat_points = sum(t[0] * t[1] for t in threats)

        dict_opp = {
            "Bullish Trend": bullish_trend,
            "Triangle Momentum": triangle_momentum,
            "Double Bot Momentum": double_bot_momentum,
            "Near Support": candle_above_dynamic_support
            or candle_above_parent_dynamic_support,
            "Candle Above Parent Static Level": candle_above_parent_static_level,
            "Candle Above Static Level": candle_above_static_Level,
            "Above Ichi": candle_ichi_above,
            "Parent Above Ichi": parent_ichi_above,
        }

        dict_threats = {
            "Bearish Trend": threat_bearish,
            "Triangle Break Down": threat_triangle,
            "Double Top Resistance": threat_double_top,
            "Grand Parent Retracement": threat_grand_parent_retrace,
            "Ichi Below Green": threat_ichi_below_green,
        }

        return dict_opp, opp_points, dict_threats, threat_points

    def buy_sell_v01(self):
        buy_pars = Parametrs()
        sell_pars = Parametrs()

        ##      Trend Status

        if self.current_trend_stat == c.Trend.Bullish:
            buy_pars.price_action_trend[1] = True
        if self.current_trend_stat == c.Trend.Bearish:
            sell_pars.price_action_trend[1] = True
        if self.ema_150_trend == c.Trend.Bullish:
            buy_pars.ema_150_trend[1] = True
        if self.ema_150_trend == c.Trend.Bearish:
            sell_pars.ema_150_trend[1] = True
        ##      Dynamic Support/Resistance Closeness

        dcst = c.Candle_Dynamic_SR_Stat
        dynamic_support_rules = [
            dcst.Close_Near_Support,
            dcst.Open_Near_Support,
            dcst.Shadow_Near_Support,
        ]
        # if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
        #     i in self.dynamic_support_stats for i in dynamic_support_rules
        # ):
        #     buy_pars.dynamic_SR_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.dynamic_support_long_stats for i in dynamic_support_rules
        ):
            buy_pars.dynamic_SR_long_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.parent_dynamic_support_stats for i in dynamic_support_rules
        ):
            buy_pars.dynamic_SR_closeness_parrent[1] = True

        dynamic_resist_rules = [
            dcst.Close_Near_Resist,
            dcst.Open_Near_Resist,
            dcst.Shadow_Near_Resist,
        ]
        # if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
        #     i in self.dynamic_resist_stats for i in dynamic_resist_rules
        # ):
        #     sell_pars.dynamic_SR_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.dynamic_resist_long_stats for i in dynamic_resist_rules
        ):
            sell_pars.dynamic_SR_long_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.parent_dynamic_resist_stats for i in dynamic_resist_rules
        ):
            sell_pars.dynamic_SR_closeness_parrent[1] = True

        ##      Static Support/Resistance Closeness

        cst = c.Candle_Level_Area_Stat
        static_support_rules = [
            cst.Closed_Near_Support,
            cst.Closed_In_Support,
            cst.Shadow_In_Support,
            cst.Shadow_Near_Support,
            cst.Opened_In_Support,
            cst.Opened_Near_Support,
        ]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.static_level_stats for i in static_support_rules
        ):
            buy_pars.static_SR_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.parent_level_stats for i in static_support_rules
        ):
            buy_pars.static_SR_closeness_parent[1] = True

        static_resist_rules = [
            cst.Closed_Near_Resist,
            cst.Closed_In_Resist,
            cst.Shadow_In_Resist,
            cst.Shadow_Near_Resist,
            cst.Opened_In_Resist,
            cst.Opened_Near_Resist,
        ]
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.static_level_stats for i in static_resist_rules
        ):
            sell_pars.static_SR_closeness[1] = True
        if (not self.candle_shapes.__contains__(c.Candle_Shape.Slim)) and any(
            i in self.parent_level_stats for i in static_resist_rules
        ):
            sell_pars.static_SR_closeness_parent[1] = True

        ##      Ichi Status

        if self.ichi_stat == c.Ichi_Stat.Above_Green:
            buy_pars.ichi_location[1] = True
        if self.ichi_parent_stat == c.Ichi_Stat.Above_Green:
            buy_pars.ichi_location_parent[1] = True
        if self.ichi_stat == c.Ichi_Stat.Below_Green:
            sell_pars.ichi_location[1] = True
        if self.ichi_parent_stat == c.Ichi_Stat.Below_Green:
            sell_pars.ichi_location_parent[1] = True

        ##     Double Bot/Top Status

        if self.double_bot_happened != 0:
            buy_pars.double_hits[1] = True
        if self.double_top_happened != 0:
            sell_pars.double_hits[1] = True

        ##      SMA 10 / 50 Status

        # if self.sma_10_50_cross_up_happened:
        #     buy_pars.sma_50_10[1] = True
        # if not self.sma_10_50_cross_up_happened:
        #     sell_pars.sma_50_10[1] = True
        # ##      EMA 5 / 10 / 30 Status

        if self.ema_5_10_30_buy_signal:
            buy_pars.ema_5_10_30[1] = True
        if self.ema_5_10_30_sell_signal:
            sell_pars.ema_5_10_30[1] = True

        ##      RSI Divergence
        if self.rsi_divergance == c.Rsi_Stat.Up:
            buy_pars.rsi_divergence[1] = True
        if self.rsi_divergance == c.Rsi_Stat.Down:
            sell_pars.rsi_divergence[1] = True
        ##      RSI Limits
        if self.rsi_over_75:
            buy_pars.rsi_cross_limits[1] = True
        if self.rsi_below_30:
            sell_pars.rsi_cross_limits[1] = True
        ##      Fibo
        if self.fibo_level_retrace_stat != c.Candle_Fibo_Stat.Nothing:
            if self.fibo_level_retrace_dir == c.Fibo_Direction.Down:
                buy_pars.fibo_retrace[1] = True
            elif self.fibo_level_retrace_dir == c.Fibo_Direction.Up:
                sell_pars.fibo_retrace[1] = True
        if self.fibo_level_trend_stat != c.Candle_Fibo_Stat.Nothing:
            if self.fibo_level_trend_dir == c.Fibo_Direction.Down:
                buy_pars.fibo_trend[1] = True
            elif self.fibo_level_trend_dir == c.Fibo_Direction.Up:
                sell_pars.fibo_trend[1] = True

        return {"buy": buy_pars, "sell": sell_pars}

    def matching_patterns(self, reversal_patterns, bullish=True):
        matching = []
        for p in reversal_patterns:
            func = getattr(talib, p)
            last_rows = self.short_term_df[-50:]
            res = (
                func(
                    last_rows["open"],
                    last_rows["high"],
                    last_rows["low"],
                    last_rows["close"],
                )
            ).reset_index()
            if bullish:
                if res[-1:][0].values[0] > 0:
                    matching.append(patterns.patterns[p])
            else:
                if res[-1:][0].values[0] < 0:
                    matching.append(patterns.patterns[p])

        return matching

    def level_bounce_position(self):
        pos = {}
        cst = c.Candle_Level_Area_Stat
        support_rules = [cst.Closed_In_Support, cst.Shadow_In_Support]
        resist_rules = [cst.Closed_In_Resist, cst.Shadow_In_Resist]
        close = self.short_term_df.iloc[-1].close
        if self.ema_150_trend == c.Trend.Bullish:
            if self.prelast_candle_static_level_stats.__contains__(
                cst.Closed_In_Support
            ) and self.prelast_candle_static_level_stats.__contains__(
                cst.Shadow_In_Support
            ):  # downtrend
                print("long first approvement")
                if self.static_level_stats.__contains__(
                    cst.Closed_Above_Support
                ) and self.static_level_stats.__contains__(cst.Opened_In_Support):
                    if (
                        self.short_term_df.low[
                            len(self.short_term_df)
                            - ac.Latest_Candles_Direction : len(self.short_term_df)
                            - 2
                        ].min()
                        > self.position_level_middle[0]
                    ):
                        tp = round(self.position_level_top[0], 4)
                        tp_percent = round(100 * (tp / close - 1), 2)
                        sl = round(self.position_level_bot[0] - tp_percent / 3, 4)
                        sl_percent = round(100 * (1 - sl / close), 2)
                        return {
                            "position": "long",
                            "name": "Static Level Bounce Back",
                            "tp": tp,
                            "sl": sl,
                            "tp_percent": tp_percent,
                            "sl_percent": sl_percent,
                            "patterns": self.matching_patterns(
                                self.bullish_reversal_patterns, bullish=True
                            ),
                        }
        if self.ema_150_trend == c.Trend.Bearish:
            if self.prelast_candle_static_level_stats.__contains__(
                cst.Closed_In_Resist
            ) and self.prelast_candle_static_level_stats.__contains__(
                cst.Shadow_In_Resist
            ):
                if self.static_level_stats.__contains__(
                    cst.Closed_Below_Resist
                ) and self.static_level_stats.__contains__(
                    cst.Opened_In_Resist
                ):  # uptrend
                    if (
                        self.short_term_df.high[
                            len(self.short_term_df)
                            - ac.Latest_Candles_Direction : len(self.short_term_df)
                            - 2
                        ].max()
                        < self.position_level_middle[1]
                    ) and self.ema_150_trend == c.Trend.Bearish:
                        # if price_threshold is satisfied
                        tp = round(self.position_level_bot[1], 4)
                        tp_percent = round(100 * (1 - tp / close), 2)
                        sl = round(
                            self.position_level_middle[1] + tp_percent / 3 / 100, 4
                        )
                        sl_percent = round(100 * (sl / close - 1), 2)
                        return {
                            "position": "short",
                            "name": "Static Level Bounce Back",
                            "tp": tp,
                            "sl": sl,
                            "tp_percent": tp_percent,
                            "sl_percent": sl_percent,
                            "patterns": self.matching_patterns(
                                self.bearish_reversal_patterns, bullish=False
                            ),
                        }
        return pos
 
    def dynamic_SR_position(self):                                         
        pos = {}
        dst = c.Candle_Dynamic_SR_Stat
        close = self.short_term_df.iloc[-1].close
        if self.ema_150_trend == c.Trend.Bullish:
            if self.dynamic_resist_long_line.__contains__(
                dst.Close_Near_Support
            ) or self.dynamic_resist_long_line.__contains__(
                dst.Shadow_Near_Support
            ):  

                tp = round(self.dynamic_last_pivots[1].high.values[0]-self.dynamic_last_pivots[0].low.values[0]+self.dynamic_last_pivots[1].high.values[0], 4)
                tp_percent = round(100 * (tp / close - 1), 2)
                sl = round(self.dynamic_last_pivots[2].low.values[0], 4)
                sl_percent = round(100 * (1 - sl / close), 2)
                return {
                    "position": "long",
                    "name": "Close to Dynamic Support",
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bullish_reversal_patterns, bullish=True
                    ),
                }
        if self.ema_150_trend == c.Trend.Bearish:
            if self.dynamic_resist_long_line.__contains__(
                dst.Close_Near_Resist
            ) or self.dynamic_resist_long_line.__contains__(
                dst.Shadow_Near_Resist
            ):  

                tp = round(self.dynamic_last_pivots[0].high.values[0]-(self.dynamic_last_pivots[0].high.values[0]-self.dynamic_last_pivots[1].low.values[0]), 4)
                tp_percent = round(100 * (tp / close - 1), 2)
                sl = round(self.dynamic_last_pivots[2].high.values[0], 4)
                sl_percent = round(100 * (1 - sl / close), 2)
                return {
                    "position": "short",
                    "name": "Close to Dynamic Resist",
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bearish_reversal_patterns, bullish=False
                    ),
                }

        return pos

    def fibo_position(self):
        fibo_retrace_short = False
        fibo_trend_short = False
        pos = {}
        close = self.short_term_df.iloc[-1].close
        if (
            self.fibo_level_retrace_dir == c.Fibo_Direction.Down
            and self.ema_150_trend == c.Trend.Bullish
        ):
            if self.fibo_level_retrace_stat == c.Candle_Fibo_Stat._618:
                fibo_retrace = True
                tp = round(self.fibo_retrace_levels[0], 4)
                tp_percent = round(100 * (tp / close - 1), 2)
                sl = round(self.fibo_retrace_levels[5], 4)
                sl_percent = round(100 * (1 - sl / close), 2)
                name = "Fib Retrace 0.618"
                if (
                    self.fibo_level_trend_dir == c.Fibo_Direction.Down
                    and self.fibo_level_trend_stat != c.Candle_Fibo_Stat.Nothing
                ):
                    name += f" + Fib Trend ({round(float(str(self.fibo_level_trend_stat).split('_')[3])/1000,3)})"
                return {
                    "position": "long",
                    "name": name,
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bullish_reversal_patterns, bullish=True
                    ),
                }
        if (
            self.fibo_level_trend_dir == c.Fibo_Direction.Down
            and self.ema_150_trend == c.Trend.Bullish
        ):
            if self.fibo_level_trend_stat == c.Candle_Fibo_Stat._618:
                tp = round(self.fibo_trend_levels[0], 4)
                tp_percent = round(100 * (tp / close - 1), 2)
                sl = round(self.fibo_trend_levels[5], 4)
                sl_percent = round(100 * (1 - sl / close), 2)
                name = "Fib Trend 0.618"
                if (
                    self.fibo_level_retrace_dir == c.Fibo_Direction.Down
                    and self.fibo_level_retrace_stat != c.Candle_Fibo_Stat.Nothing
                ):
                    name += f" + Fib Retrace ({round(float(str(self.fibo_level_retrace_stat).split('_')[3])/1000,3)})"

                return {
                    "position": "long",
                    "name": name,
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bullish_reversal_patterns, bullish=True
                    ),
                }
        if (
            self.fibo_level_retrace_dir == c.Fibo_Direction.Up
            and self.ema_150_trend == c.Trend.Bearish
        ):
            if self.fibo_level_retrace_stat == c.Candle_Fibo_Stat._618:
                tp = round(self.fibo_retrace_levels[0], 4)
                tp_percent = round(100 * (1 - tp / close), 2)
                sl = round(self.fibo_retrace_levels[5], 4)
                sl_percent = round(100 * (sl / close - 1), 2)
                name = "Fib Retrace 0.618"
                if (
                    self.fibo_level_trend_dir == c.Fibo_Direction.Up
                    and self.fibo_level_trend_stat != c.Candle_Fibo_Stat.Nothing
                ):
                    name += f" + Fib Trend ({round(float(str(self.fibo_level_trend_stat).split('_')[3])/1000,3)})"

                return {
                    "position": "short",
                    "name": name,
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bullish_reversal_patterns, bullish=False
                    ),
                }
        if (
            self.fibo_level_trend_dir == c.Fibo_Direction.Up
            and self.ema_150_trend == c.Trend.Bearish
        ):
            if self.fibo_level_trend_stat == c.Candle_Fibo_Stat._618:
                tp = round(self.fibo_trend_levels[0], 4)
                tp_percent = round(100 * (1 - tp / close), 2)
                sl = round(self.fibo_trend_levels[5], 4)
                sl_percent = round(100 * (sl / close - 1), 2)
                name = "Fib Trend 0.618"
                if (
                    self.fibo_level_retrace_dir == c.Fibo_Direction.Up
                    and self.fibo_level_retrace_stat != c.Candle_Fibo_Stat.Nothing
                ):
                    name += f" + Fib Retrace ({round(float(str(self.fibo_level_retrace_stat).split('_')[3])/1000,3)})"

                return {
                    "position": "short",
                    "name": name,
                    "tp": tp,
                    "sl": sl,
                    "tp_percent": tp_percent,
                    "sl_percent": sl_percent,
                    "patterns": self.matching_patterns(
                        self.bullish_reversal_patterns, bullish=False
                    ),
                }

        return pos

    def features(self):
        dcst = c.Candle_Dynamic_SR_Stat
        cst = c.Candle_Level_Area_Stat
        parent_dict = {}
        # if self.dynamic_support_candle_location_parent:
        #     parent_dict={
        #         "Closed_In_Support_Parent":[(self.parent_static_levels.__contains__(cst.Closed_In_Support))],
        #         "Closed_Near_Support_Parent":[(self.parent_static_levels.__contains__(cst.Closed_Near_Support))],
        #         "Shadow_In_Support_Parent":[(self.parent_static_levels.__contains__(cst.Shadow_In_Support))],
        #         "Shadow_Near_Support_s_Parent":[(self.parent_static_levels.__contains__(cst.Shadow_Near_Support))], # "_s" stands for "Static"
        #         "Opened_In_Support_Parent":[(self.parent_static_levels.__contains__(cst.Opened_In_Support))],
        #         "Opened_Near_Support_Parent":[(self.parent_static_levels.__contains__(cst.Opened_Near_Support))],

        #         "Closed_In_Resist_Parent":[(self.parent_static_levels.__contains__(cst.Closed_In_Resist))],
        #         "Closed_Near_Resist_Parent":[(self.parent_static_levels.__contains__(cst.Closed_Near_Resist))],
        #         "Shadow_In_Resist_Parent":[(self.parent_static_levels.__contains__(cst.Shadow_In_Resist))],
        #         "Shadow_Near_Resist_s_Parent":[(self.parent_static_levels.__contains__(cst.Shadow_Near_Resist))], # "_s" stands for "Static"
        #         "Opened_In_Resist_Parent":[(self.parent_static_levels.__contains__(cst.Opened_In_Resist))],
        #         "Opened_Near_Resist_Parent":[(self.parent_static_levels.__contains__(cst.Opened_Near_Resist))],

        #         "Candle_Close_Loc_To_Dynamic_Support_Parent":[self.dynamic_support_candle_location_parent['close']],
        #         "Candle_Open_Loc_To_Dynamic_Support_Parent":[self.dynamic_support_candle_location_parent['open']],
        #         "Candle_High_Loc_To_Dynamic_Support_Parent":[self.dynamic_support_candle_location_parent['high']],
        #         "Candle_Low_Loc_To_Dynamic_Support_Parent":[self.dynamic_support_candle_location_parent['low']],

        #         "Candle_Close_Loc_To_Dynamic_Resist_Parent":[self.dynamic_resist_candle_location_parent['close']],
        #         "Candle_Open_Loc_To_Dynamic_Resist_Parent":[self.dynamic_resist_candle_location_parent['open']],
        #         "Candle_High_Loc_To_Dynamic_Resist_Parent":[self.dynamic_resist_candle_location_parent['high']],
        #         "Candle_Low_Loc_To_Dynamic_Resist_Parent":[self.dynamic_resist_candle_location_parent['low']]
        #     }
        f = {
            "current_trend": [self.current_trend_stat.value],
            "Candle_Shape_Normal": [
                (self.candle_shapes.__contains__(c.Candle_Shape.Normal))
            ],
            "Candle_Shape_Small": [
                (self.candle_shapes.__contains__(c.Candle_Shape.Small))
            ],
            "Candle_Shape_Strong": [
                (self.candle_shapes.__contains__(c.Candle_Shape.Strong))
            ],
            "Candle_Shape_Slim": [
                (self.candle_shapes.__contains__(c.Candle_Shape.Slim))
            ],
            "Candle_Shape_Point": [
                (self.candle_shapes.__contains__(c.Candle_Shape.Point))
            ],
            "Candle_Shape_PinBar_Up": [
                (self.candle_shapes.__contains__(c.Candle_Shape.PinBar_Up))
            ],
            "Candle_Shape_PinBar_Down": [
                (self.candle_shapes.__contains__(c.Candle_Shape.PinBar_Down))
            ],
            "Closed_In_Support": [
                (self.static_level_stats.__contains__(cst.Closed_In_Support))
            ],
            "Closed_Near_Support": [
                (self.static_level_stats.__contains__(cst.Closed_Near_Support))
            ],
            "Shadow_In_Support": [
                (self.static_level_stats.__contains__(cst.Shadow_In_Support))
            ],
            "Shadow_Near_Support_s": [
                (self.static_level_stats.__contains__(cst.Shadow_Near_Support))
            ],  # "_s" stands for "Static"
            "Opened_In_Support": [
                (self.static_level_stats.__contains__(cst.Opened_In_Support))
            ],
            "Opened_Near_Support": [
                (self.static_level_stats.__contains__(cst.Opened_Near_Support))
            ],
            "Closed_In_Resist": [
                (self.static_level_stats.__contains__(cst.Closed_In_Resist))
            ],
            "Closed_Near_Resist": [
                (self.static_level_stats.__contains__(cst.Closed_Near_Resist))
            ],
            "Shadow_In_Resist": [
                (self.static_level_stats.__contains__(cst.Shadow_In_Resist))
            ],
            "Shadow_Near_Resist_s": [
                (self.static_level_stats.__contains__(cst.Shadow_Near_Resist))
            ],  # "_s" stands for "Static"
            "Opened_In_Resist": [
                (self.static_level_stats.__contains__(cst.Opened_In_Resist))
            ],
            "Opened_Near_Resist": [
                (self.static_level_stats.__contains__(cst.Opened_Near_Resist))
            ],
            #    "Close_Near_Support":[(self.dynamic_support_stats.__contains__(dcst.Close_Near_Support))],
            #    "Open_Near_Support":[(self.dynamic_support_stats.__contains__(dcst.Open_Near_Support))],
            #    "Shadow_Near_Support":[(self.dynamic_support_stats.__contains__(dcst.Shadow_Near_Support))],
            #    "Close_Near_Resist":[(self.dynamic_support_stats.__contains__(dcst.Close_Near_Resist))],
            #    "Open_Near_Resist":[(self.dynamic_support_stats.__contains__(dcst.Open_Near_Resist))],
            #    "Shadow_Near_Resist":[(self.dynamic_support_stats.__contains__(dcst.Shadow_Near_Resist))],
            # # # "Candle_Close_Loc_To_Dynamic_Support": [
            # # #     self.dynamic_support_candle_location["close"]
            # # # ],
            # # # "Candle_Open_Loc_To_Dynamic_Support": [
            # # #     self.dynamic_support_candle_location["open"]
            # # # ],
            # # # "Candle_High_Loc_To_Dynamic_Support": [
            # # #     self.dynamic_support_candle_location["high"]
            # # # ],
            # # # "Candle_Low_Loc_To_Dynamic_Support": [
            # # #     self.dynamic_support_candle_location["low"]
            # # # ],
            # # # "Candle_Close_Loc_To_Dynamic_Resist": [
            # # #     self.dynamic_resist_candle_location["close"]
            # # # ],
            # # # "Candle_Open_Loc_To_Dynamic_Resist": [
            # # #     self.dynamic_resist_candle_location["open"]
            # # # ],
            # # # "Candle_High_Loc_To_Dynamic_Resist": [
            # # #     self.dynamic_resist_candle_location["high"]
            # # # ],
            # # # "Candle_Low_Loc_To_Dynamic_Resist": [
            # # #     self.dynamic_resist_candle_location["low"]
            # # # ],
            "Candle_Close_Loc_To_Dynamic_Support_Long": [
                self.dynamic_support_long_candle_location["close"]
            ],
            "Candle_Open_Loc_To_Dynamic_Support_Long": [
                self.dynamic_support_long_candle_location["open"]
            ],
            "Candle_High_Loc_To_Dynamic_Support_Long": [
                self.dynamic_support_long_candle_location["high"]
            ],
            "Candle_Low_Loc_To_Dynamic_Support_Long": [
                self.dynamic_support_long_candle_location["low"]
            ],
            "Candle_Close_Loc_To_Dynamic_Resist_Long": [
                self.dynamic_resist_long_candle_location["close"]
            ],
            "Candle_Open_Loc_To_Dynamic_Resist_Long": [
                self.dynamic_resist_long_candle_location["open"]
            ],
            "Candle_High_Loc_To_Dynamic_Resist_Long": [
                self.dynamic_resist_long_candle_location["high"]
            ],
            "Candle_Low_Loc_To_Dynamic_Resist_Long": [
                self.dynamic_resist_long_candle_location["low"]
            ],
            "Ichi_Stat": [self.ichi_stat.value],
            "double_bot": [self.double_bot_happened],
            "double_top": [self.double_top_happened],
            # "sma_10_50": [(self.sma_10_50_cross_up_happened)],
            "ema_5_10_30_buy_signal": [(self.ema_5_10_30_buy_signal)],
            "ema_5_10_30_sell_signal": [(self.ema_5_10_30_sell_signal)],
            #   "rsi_divergence":[self.rsi_divergance.value],
            #    "rsi_over_75":[self.rsi_over_75],
            #    "rsi_below_30":[self.rsi_below_30],
            "rsi": [self.rsi],
            "fibo_level_retrace_stat": [self.fibo_level_retrace_stat.value],
            "fibo_level_retrace_dir": [self.fibo_level_retrace_dir.value],
            "fibo_level_trend_stat": [self.fibo_level_trend_stat.value],
            "fibo_level_trend_dir": [self.fibo_level_trend_dir.value],
            "Candle_Close_Loc_To_Dynamic_Bollinger_Top": [
                self.bollinger_top_candle_location["close"]
            ],
            "Candle_Open_Loc_To_Dynamic_Bollinger_Top": [
                self.bollinger_top_candle_location["open"]
            ],
            "Candle_High_Loc_To_Dynamic_Bollinger_Top": [
                self.bollinger_top_candle_location["high"]
            ],
            "Candle_Low_Loc_To_Dynamic_Bollinger_Top": [
                self.bollinger_top_candle_location["low"]
            ],
            "Candle_Close_Loc_To_Dynamic_Bollinger_Bot": [
                self.bollinger_bot_candle_location["close"]
            ],
            "Candle_Open_Loc_To_Dynamic_Bollinger_Bot": [
                self.bollinger_bot_candle_location["open"]
            ],
            "Candle_High_Loc_To_Dynamic_Bollinger_Bot": [
                self.bollinger_bot_candle_location["high"]
            ],
            "Candle_Low_Loc_To_Dynamic_Bollinger_Bot": [
                self.bollinger_bot_candle_location["low"]
            ],
        }
        if parent_dict:
            f.update(parent_dict)
        return f
