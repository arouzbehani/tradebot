import MarketReader as mr
import signaler as sg

testdata = False
relpath = True
read_patterns = False
tf = '30m'
delay = 1*24*60
brout_candles = 15
brout_percentage = 2

#mr.ReadKucoinMarket([tf], testdata=testdata, relp=relpath)
sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', relp=relpath, testdata=testdata),
                       exchangeName='Kucoin', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
