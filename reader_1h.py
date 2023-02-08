import strl.MarketReader as mr
import signaler as sg

testdata = False
<<<<<<< HEAD
local = False
=======
relpath = True
>>>>>>> 53244542e91a989b72c20f68ef4f11302afe3df2
read_patterns = False
tf = '1h'
delay = 3*24*60
brout_candles = 15
brout_percentage = 2

<<<<<<< HEAD
mr.ReadKucoinMarket([tf], testdata=testdata, local=local)
sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', local=local, testdata=testdata),
                     exchangeName='Kucoin', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadYahooMarket(['60m'],testdata=testdata,local=local)
sg.TALibPattenrSignals(delay, ['60m'], markets=mr.GetMarkets('60m', exchangeName='Yahoo', local=local, testdata=testdata),
                       exchangeName='Yahoo', local=local, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
=======
#mr.ReadKucoinMarket([tf], testdata=testdata, relp=relpath)
#sg.TALibPattenrSignals(delay, [tf], markets=mr.GetMarkets(tf, exchangeName='Kucoin', relp=relpath, testdata=testdata),
#                       exchangeName='Kucoin', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)

mr.ReadYahooMarket(['60m'],testdata=testdata,local=relpath)
sg.TALibPattenrSignals(delay, ['60m'], markets=mr.GetMarkets('60m', exchangeName='Yahoo', relp=relpath, testdata=testdata),
                       exchangeName='Yahoo', relp=relpath, brout_candles=brout_candles, brout_percentage=brout_percentage, read_patterns=read_patterns)
>>>>>>> 53244542e91a989b72c20f68ef4f11302afe3df2
