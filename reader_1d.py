import MarketReader as mr
import signaler as sg

testdata = False
relpath = False
tf = '1d'
delay = 7*24*60
brout_candles = 15
brout_percentage = 2

mr.ReadKucoinMarket([tf], testdata=testdata, relp=relpath)
sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', relp=relpath),
                       exchangeName='Kucoin', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage)
