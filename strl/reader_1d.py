import config,helper
import MarketReader as mr
import signaler as sg
import datetime , calendar

testdata = False
local=helper.GetLocal()
read_patterns = False
tf = '1d'
delay = 14*24*60
brout_candles = 15
brout_percentage = 2

# mr.ReadKucoinMarket([tf], testdata=testdata, local=local)
# # sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
# #                        exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

# weekday=datetime.datetime.now().weekday()
# dayname=calendar.day_name[weekday]

# if (dayname !='Saturday' and dayname!='Sunday'):
#     mr.ReadYahooMarket(['1d', '1wk'], testdata=testdata, local=local)
#     # sg.TALibPattenrSignals(delay, ['1d'], markets=mr.GetMarkets('1d', exchangeName='Yahoo', local=local, testdata=testdata),
#     #                     exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadForexMarket(['1day'], testdata=testdata,local=local,symbol='',secrets=[config.Tiingo_Secrets['rouzbehani']])
