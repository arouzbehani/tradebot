import MarketReader as mr
import signaler as sg

testdata=False
relpath=False
tf='1h'
delay=1*24*60

mr.ReadKucoinMarket([tf],testdata= testdata,relp=relpath)
sg.TALibPattenrSignals(delay,[tf],markets=mr.GetMarkets(tf,exchangeName='Kucoin',relp=relpath),exchangeName='Kucoin',relp=relpath)
