import MarketReader as mr
import signaler as sg
import datetime , calendar

testdata = False
import subprocess
interface = "eth0"
ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
local = ip !='51.89.178.202'
read_patterns = False
tf = '4h'
delay = 4*24*60
brout_candles = 15
brout_percentage = 2

mr.ReadKucoinMarket([tf], testdata=testdata, local=local)
# sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
#                        exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)


weekday=datetime.datetime.now().weekday()
dayname=calendar.day_name[weekday]

if (dayname !='Saturday' and dayname!='Sunday'):
    mr.ReadYahooMarket(['90m'],testdata=testdata,local=local)
    # sg.TALibPattenrSignals(delay, ['90m'], markets=mr.GetMarkets('90m', exchangeName='Yahoo', local=local, testdata=testdata),
    #                     exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
