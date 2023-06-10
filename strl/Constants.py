import enum

class Candle_Color(enum.Enum):
   Green=1
   Red=2
class Candle_Shape(enum.Enum):
   Normal=1
   PinBar_Up=2
   PinBar_Down=2
   Strong=4
   Point=5
   Slim=6
   Small=7

class SMA_Stat(enum.Enum):
   Nothing=0
   CrossUp=1
   CrossDown=2


class Trend(enum.Enum):
   Nothing=0
   Bearish = 1
   Bullish = 2
   Widening_Side=3
   Narrowing_Side=4

class PA_Break(enum.Enum):
   Nothing=0
   Bearish_Break_Up=1
   Bullish_Break_Down=2

class Trend_SR_Stat(enum.Enum):
   Nothing =0
   Fit_Support=1
   Fit_Resist=2
class Ichi_Stat(enum.Enum):
   Nothing =0
   Below_Red=1
   Above_Red=2
   Below_Green=3
   Above_Green=4
   Inside_Red=5
   Inside_Green=6
   Error=7
class Candle_Dynamic_SR_Stat(enum.Enum):
   Nothing=0
   Open_Near_Support=1
   Close_Near_Support=2
   Shadow_Near_Support=3
   Open_Near_Resist=4
   Close_Near_Resist=5
   Shadow_Near_Resist=6
   
class Candle_Level_Area_Stat(enum.Enum):
   Nothing=0
   Closed_In_Support=1
   Closed_In_Resist=2
   Opened_In_Support=3
   Opened_In_Resist=4  
   Shadow_In_Support=5
   Shadow_In_Resist=6
   Closed_Near_Support=7
   Closed_Near_Resist=8
   Opened_Near_Support=9
   Opened_Near_Resist=10
   Shadow_Near_Support=11
   Shadow_Near_Resist=12


class Candle_Cross_Level_Stat(enum.Enum):
   Nothing=0
   Break_Up=1
   Break_down=2

class Candle_Channel_Stat(enum.Enum):
   Nothing=0
   Break_Up=1
   Break_Down=2
   Near_Resistant=3
   Near_Support=4

class Candle_Fibo_Stat(enum.Enum):
   Nothing=-1
   _0=0
   _382=1
   _500=2
   _618=3
   _786=4
   _1000=5
   _1618=6
   _2618=7

class Candles_Direction(enum.Enum):
   Side=0
   Bullish=1
   Bearish=2

class Fibo_Mode(enum.Enum):
   Retracement=1
   Trend_Base_Extension=2

class Fibo_Direction(enum.Enum):
   Down=1
   Up=2

class Rsi_Stat(enum.Enum):
   Nothing=0
   Up=1
   Down=2