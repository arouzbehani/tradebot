import MarketReader as mr
import scanner
import datetime , calendar
import top_100_crypto
import config

testdata = False
import subprocess
interface = "eth0"
local=False
try:
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !='51.89.178.202'
except:
    local=True
read_patterns = False
tf = '1h'
delay = 100*24*60
brout_candles = 15
brout_percentage = 2

# # featured_symbols=scanner.Get_FeaturedSymbols(exch='Kucoin',tf='1h')
# mr.ReadKucoinMarket(['1h','15m'], testdata=testdata, local=local,featured_symbols=top_100_crypto.top100)
# scanner.Position_Scan(exch='Kucoin',tf='1h',tfs=['4h','1h','15m'])
# # mr.ReadKucoinMarket(['5m'], testdata=testdata, local=local,featured_symbols=top_100_crypto.top100)
# # scanner.Position_Scan(exch='Kucoin',tf='15m',tfs=['1h','15m','5m'])
# mr.ReadKucoinMarket(['15m','1h'], testdata=testdata, local=local,except_symbols=top_100_crypto.top100)

# # sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
# #                      exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)


# weekday=datetime.datetime.now().weekday()
# dayname=calendar.day_name[weekday]

# if (dayname !='Saturday' and dayname!='Sunday'):

#     mr.ReadYahooMarket(['60m','15m'],testdata=testdata,local=local)
#     # sg.TALibPattenrSignals(delay, ['60m'], markets=mr.GetMarkets('60m', exchangeName='Yahoo', local=local, testdata=testdata),
#     #                        exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadForexMarket(['15min','1Hour'], testdata=testdata,local=local,symbol='',secrets=[config.Tiingo_Secrets['roozg'],config.Tiingo_Secrets['baharsoft']])
scanner.Position_Scan(exch='Forex',tf='1Hour',tfs=['4Hour','1Hour','15min'])
