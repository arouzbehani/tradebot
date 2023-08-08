from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

def DrawCandleSticks(df,df2,both=True,symbol='BTC_USDT',rownum=2):
        
    row_heights = [0.7]
    for k in range(0, rownum-1):
        row_heights.append(0.4/(rownum-1))        
        fig = make_subplots(
        rows=rownum, cols=1,
        column_widths=[1],
        row_heights=row_heights,
        shared_xaxes=True, vertical_spacing=0.01)

        if both:

            fig.add_trace(
                go.Candlestick(x=df['time'], open=df['open'], close=df['close'], high=df['high'], low=df['low'], name=symbol.replace('_', '/')), row=1, col=1
            )    
            pointpos_df = pd.DataFrame(
                data=df[~pd.isnull(df['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
            pointpos_df2 = pd.DataFrame(
                data=df2[~pd.isnull(df2['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])

            fig.add_trace(
                go.Scatter(x=pointpos_df['time'], y=pointpos_df['pointpos'], line=dict(
                    color="#3d5ab2"), name='long term wave line')
            )
            fig.add_trace(
                go.Scatter(x=pointpos_df2['time'], y=pointpos_df2['pointpos'], line=dict(
                    color="#9999ff"), name='short term wave line')
            )    
            return fig
        else:
            fig.add_trace(
                go.Candlestick(x=df2['time'], open=df2['open'], close=df2['close'], high=df2['high'], low=df2['low'], name=symbol.replace('_', '/')), row=1, col=1
            )    
            pointpos_df2 = pd.DataFrame(
                data=df2[~pd.isnull(df2['pointpos'])], columns=['time', 'pointpos', 'pivot', 'timestamp'])
            fig.add_trace(
                go.Scatter(x=pointpos_df2['time'], y=pointpos_df2['pointpos'], line=dict(
                    color="#9999ff"), name='short term wave line')
            )    
            return fig


def AppendLineChart(fig,xs,ys,row=1,col=1,line=dict(width=1) , name='trace'):
    fig.add_trace(
        go.Scatter(x=xs, y=ys, name=name, line=line, mode='lines'), row=row, col=col
    )
    
def AppendPointChart(fig,xs,ys,row=1,col=1,size=10, color="red", symbol='star',name=''):
    marker=dict(size=size, color=color, symbol=symbol)
    fig.add_trace(
    go.Scatter(x=xs, y=ys, name=name, mode='markers', marker=marker)
    , row=row, col=col)