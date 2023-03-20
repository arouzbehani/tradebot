import MarketReader as mr
import signaler as sg
import datetime , calendar

testdata = True
local = True
read_patterns = False
tf = '1h'
delay = 100*24*60
brout_candles = 15
brout_percentage = 2

#mr.ReadKucoinMarket([tf], testdata=testdata, local=local)
sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
                     exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)


# weekday=datetime.datetime.now().weekday()
# dayname=calendar.day_name[weekday]

# if (dayname !='Saturday' and dayname!='Sunday'):

#     mr.ReadYahooMarket(['60m'],testdata=testdata,local=local)
#     sg.TALibPattenrSignals(delay, ['60m'], markets=mr.GetMarkets('60m', exchangeName='Yahoo', local=local, testdata=testdata),
#                            exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
