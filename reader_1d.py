import MarketReader as mr
import signaler as sg

testdata = False
local = False
read_patterns = False
tf = '1d'
delay = 14*24*60
brout_candles = 15
brout_percentage = 2

mr.ReadKucoinMarket([tf], testdata=testdata, relp=local)
sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', relp=local, testdata=testdata),
                       exchangeName='Kucoin', relp=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadYahooMarket(['1d','1wk'],testdata=testdata,local=local)
sg.TALibPattenrSignals(delay, ['1d'], markets=mr.GetMarkets('1d', exchangeName='Yahoo', relp=local, testdata=testdata),
                       exchangeName='Yahoo', relp=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
