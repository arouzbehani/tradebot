import MarketReader as mr
import signaler as sg
import datetime , calendar

testdata = False
local = False
read_patterns = False
tf = '30m'
delay = 5*24*60
brout_candles = 15
brout_percentage = 2

mr.ReadKucoinMarket(['15m','30m'], testdata=testdata, local=local)
sg.TALibPattenrSignals(delay, ['30m'], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
                       exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

weekday=datetime.datetime.now().weekday()
dayname=calendar.day_name[weekday]

if (dayname !='Saturday' or dayname!='Sunday'):
    mr.ReadYahooMarket(['15m','30m'],testdata=testdata,local=local)
    sg.TALibPattenrSignals(delay, ['30m'], markets=mr.GetMarkets('30m', exchangeName='Yahoo', local=local, testdata=testdata),
                        exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
