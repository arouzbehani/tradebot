import config,helper
import MarketReader as mr
import signaler as sg
import datetime , calendar
import scanner

testdata = False

local=helper.GetLocal()
read_patterns = False
tf = '4h'
delay = 4*24*60
brout_candles = 15
brout_percentage = 2


# # featured_symbols=scanner.Get_FeaturedSymbols(exch='Kucoin',tf='4h')
# # mr.ReadKucoinMarket(['4h'], testdata=testdata, local=local,featured_symbols=featured_symbols)
# # scanner.ML_Scan(exch='Kucoin',pref_tf='4h')

# mr.ReadKucoinMarket([tf], testdata=testdata, local=local)
# # sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
# #                        exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)


# weekday=datetime.datetime.now().weekday()
# dayname=calendar.day_name[weekday]

# if (dayname !='Saturday' and dayname!='Sunday'):
#     mr.ReadYahooMarket(['90m'],testdata=testdata,local=local)
#     # sg.TALibPattenrSignals(delay, ['90m'], markets=mr.GetMarkets('90m', exchangeName='Yahoo', local=local, testdata=testdata),
#     #                     exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadForexMarket(['4Hour'], testdata=testdata,local=local,symbol='',secrets=[config.Tiingo_Secrets['oned']])
scanner.Position_Scan(exch='Forex',tf='4Hour',tfs=['1day','4Hour','1Hour'])
