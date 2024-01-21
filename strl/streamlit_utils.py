import streamlit as st
import top_100_crypto
import MarketReader as mr
def rerun():
    st.experimental_rerun()
    
def getTilte(title='Chart'):
    q = st.experimental_get_query_params()
    if q.__contains__("symbol"):
        return f'{q["symbol"][0]} {title}'
    return title
global symbol,tf,exch,markets,indexed_symbol
symbol = None
tf = None
exch = None
q = st.experimental_get_query_params()
if q.__contains__("symbol"):
    symbol = q["symbol"][0]
if q.__contains__("tf"):
    tf = q["tf"][0]
if q.__contains__("exch"):
    exch = q["exch"][0]
base_urls={'forex':'https://bingx.com/en-us/futures/forex',
        'yahoo':'https://bingx.com/en-us/futures/forward',
        'kucoin':'https://bingx.com/en-us/futures/forward'}  
markets=[]
indexed_symbol=''

def set_page_config(local=False,title='Chart'):
    st.set_page_config(layout="wide", page_title=getTilte(title=title))
    st.markdown(
        """

            <style>
                    ..css-k1ih3n {
                        padding: 0;
                    }

            </style>
            """,
        unsafe_allow_html=True,
    )

    if (symbol != None):
        if exch=='Forex':
            markets=mr.forex_market.GetMarkets(local=local)
            indexed_symbol=symbol.replace('_','/')
        if exch=='Kucoin':
            markets=top_100_crypto.top100
            indexed_symbol=symbol
        if exch=='Yahoo':
            markets=mr.ym.GetMarkets(local=local)
            indexed_symbol=symbol
    

    url = '{}/{}'.format(
        base_urls[exch.lower()],symbol.replace('_', '').upper())
    link = (st.markdown(f'''
    <a href={url}><button style="background-color:transparent;border:none;text-decoration: underline; color:#21a58a; font-size:large">View {symbol.replace('_','/')} Chart on BingX</button></a>
    ''',
                        unsafe_allow_html=True))
