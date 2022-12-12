import MarketReader as mr
import signaler as sg

testdata=False
relpath=False
tf='4h'
delay=4*24*60

mr.ReadKucoinMarket([tf],testdata= testdata,relp=relpath)
sg.TALibPattenrSignals(delay,[tf],markets=mr.GetMarkets(tf,exchangeName='Kucoin',relp=relpath),exchangeName='Kucoin',relp=relpath)
