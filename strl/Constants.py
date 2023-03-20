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
   Above=1
   Below=2


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
   Open_Above_Support=1
   Close_Above_Support=2
   High_Above_Support=3
   Low_Above_Support=4
   Open_Above_Resist=5
   Close_Above_Resist=6
   High_Above_Resist=7
   Low_Above_Resist=8

   Open_Below_Support=9
   Close_Below_Support=10
   High_Below_Support=11
   Low_Below_Support=12
   Open_Below_Resist=13
   Close_Below_Resist=14
   High_Below_Resist=15
   Low_Below_Resist=16 
   
class Candle_Level_Area_Stat(enum.Enum):
   Nothing=0
   Closed_In_Support=1
   Closed_In_Resist=2
   Touched_Support=3
   Touched_Resist=4
   Broke_Support=5
   Near_Support=6
   Broke_Resist=7
   Near_Resist=8

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

class Fibo_Mode(enum.Enum):
   Retracement=1
   Trend_Base_Extension=2

class Fibo_Direction(enum.Enum):
   Down=1
   Up=2