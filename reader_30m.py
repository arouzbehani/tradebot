import MarketReader as mr
import signaler as sg

testdata = False
relpath = True
read_patterns = False
tf = '30m'
delay = 5*24*60
brout_candles = 15
brout_percentage = 2

mr.ReadKucoinMarket(['15m','30m'], testdata=testdata, relp=relpath)
sg.TALibPattenrSignals(delay, ['30m'], markets=mr.GetMarkets(tf, exchangeName='Kucoin', relp=relpath, testdata=testdata),
                       exchangeName='Kucoin', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadYahooMarket(['15m','30m'],testdata=testdata,local=relpath)
sg.TALibPattenrSignals(delay, ['30m'], markets=mr.GetMarkets('30m', exchangeName='Yahoo', relp=relpath, testdata=testdata),
                       exchangeName='Yahoo', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
