import os , gc
import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import datetime , calendar

def clean(obj):
    del obj
    gc.collect()
    return obj
# def GetData():
#     data = {'1h':[], '1d':[] , '30m':[],'4h':[]}
#     for tf in data:
#         res , df=sg.TALibPattenrSignals(7*24*60,[tf])
#         if( res ==True):
#             data[tf].append(df)
#             print("{} done!".format(tf))

#     return data

# def talib():
    # data = GetData()
    # if (len(data) > 0):
    #     tables = {'1h': [],
    #                 '4h': [],
    #                 '30m': [],
    #                 '1d': []}
    #     for d in data:
    #         if(len(data[d])>0):
    #             pretty_bullish = data[d][0][[
    #                 'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
    #             pretty_bearish = data[d][0][[
    #                 'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
    #             tables[d].append(HTML(pretty_bullish.to_html(classes='table table-hovered')))
    #             tables[d].append(HTML(pretty_bearish.to_html(classes='table table-hovered')))
    # print(tables)

def getTestData(exch='kucoin',coin='BTC_USDT',tf='1h'):
    rel_path = 'Market Data/{}/{}/{}__{}.csv'.format(exch,tf,coin,tf)
    return pd.read_csv(rel_path)



# def GetData0():
#     BASE_DIR = '/root/trader_webapp'
#     data = {'1h':[], '1d':[] , '30m':[],'4h':[]}
#     for tf in data:
#         rel_path = 'TA-Lib Signals/'+tf+'/'
#         abs_dir = os.path.join(BASE_DIR, rel_path)
#         abs_dir=rel_path
#         paths = sorted(Path(abs_dir).iterdir(), key=os.path.getmtime)
#         for path in paths:
#             df = pd.read_csv(path)
#             data[tf].append(df)
#     return data

# def signals():
#     data = GetData0()
#     # data[0]['Trading View']=data[0]['Coin'].map(tourl)
#     if (len(data) > 0):
#         tables = {'1h': [],
#                     '4h': [],
#                     '30m': [],
#                     '1d': []}
#         for d in data:
#             if(data[d]):
#                 pretty_bullish = data[d][len(data[d])-1][[
#                     'Coin', 'date time', 'bullish', 'bullish patterns']].sort_values(by=['bullish'], ascending=False)
#                 pretty_bearish = data[d][len(data[d])-1][[
#                     'Coin', 'date time', 'bearish', 'bearish patterns']].sort_values(by=['bearish'], ascending=False)
#                 tables[d].append(HTML(pretty_bullish.to_html(classes='table table-hovered')))
#                 tables[d].append(HTML(pretty_bearish.to_html(classes='table table-hovered')))

#     print(tables)

# def arraytest():
#     l=[1,2,3,4,5,6,7,8,9,10]
#     print(f"list -->{l}")
#     print(f"l[:-1] -->{l[:-1]}")
#     print(f"l[-1:] -->{l[-1:]}")
#     print(f"l[-2:-1] -->{l[-2:-1]}")
#     print(f"l[-1] -->{l[-1]}")
# def BollingerView():
#     df=getMarketData(coin='BTC_USDT')
    
#     indicator_bb = bb(close=df['close'], window=20,
#             window_dev=2, fillna=False)
#     df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
#     df['upperband'] = indicator_bb.bollinger_hband()
#     df['middleband'] = indicator_bb.bollinger_mavg()
#     df['lowerband'] = indicator_bb.bollinger_lband()
#     df['pband'] = indicator_bb.bollinger_pband()
#     pd.set_option('display.max_rows', 1000)

#     print(pd.DataFrame(df , columns=['date','pband']))
# #BollingerView()
# def arrayshow():
#     list=[1,2,3,4,5,6,7,8,9,10]
#     print(list[:len(list)-3])
# # arrayshow()
# def is_consolidating(closes, percentage=2):
#     max_close=closes.max()
#     min_close=closes.min()
#     threshold=1-(percentage/100)
#     if min_close > (max_close * threshold):
#         return True
#     return False
# def brout_check(df,candles=15):
#     for index in df.index:
#         if (index>=candles):
#             last_close=df['close'][index]
#             if (is_consolidating(df['close'][index-candles-1:index-1],percentage=10)):
#                 if(last_close>df['close'][index-candles-1:index-1].max()):
#                     df['brout'][index]=1
#                 else:
#                     df['brout'][index]=np.nan
#             else:
#                     df['brout'][index]=np.nan
#         else:
#             df['brout'][index]=np.nan
            
#     return df
# # df=getMarketData(tf='30m',coin='Theta_USDT')
# # fi_indicator=fi(close =df['close'],volume=df['volume'],window=100,fillna=False)
# # df['fi']=fi_indicator.force_index()
# # vol_mean=(df['fi'].max()+abs(df['fi'].min()))/2
# # print(f"max:{df['fi'].max()/vol_mean} min:{df['fi'].min()/vol_mean}")
# # df1=df.reset_index()
# # df1['brout']=np.nan
# # #st.dataframe(df['close'][18-15:18].min())
# # df2=brout_check(df1,candles=15)
# # print(df2)
# # cmc = CoinMarketCapAPI(api_key=config.CoinMarketCap_API_Key)
# # rep = cmc.cryptocurrency_trending_latest()
# # print(rep)
# # def set_output(o):
# #     if not (str(o).__contains__('Hi Sai')):
# #          return "No value found"
# #     return o
# # data = {'ID': ['1', '2', '3', '4'],'Name header':['John','Ahmad','Neli','Hamid'],'Output':['Hi Sai sasasdasd','output 2','112123 Hi Sai','output 4']}
# # df = pd.DataFrame(data)
# # df['Output']=df['Output'].map(set_output)
# # print (df)
 
# # msft = yf.Ticker("MSFT")
# # data = yf.download("MSFT", start="2022-01-01", end="2022-01-30")
# # hist = msft.history(period="1wk")

# # print(hist)
# # print(data)
#define data
# # # # from statistics import mean
# # # # import numpy as np
# # # # import matplotlib.pyplot as plt
# # # # from matplotlib import style
# # # # style.use('ggplot')

# # # # xs = np.array([1,2,3,4,5], dtype=np.float64)
# # # # ys = np.array([5,6,17,18,91], dtype=np.float64)

# # # # def best_fit_slope_and_intercept(xs,ys):
# # # #     m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
# # # #          ((mean(xs)*mean(xs)) - mean(xs*xs)))
# # # #     b = mean(ys) - m*mean(xs)
# # # #     return m, b

# # # # def squared_error(ys_orig,ys_line):
# # # #     return sum((ys_line - ys_orig) * (ys_line - ys_orig))

# # # # def coefficient_of_determination(ys_orig,ys_line):
# # # #     y_mean_line = [mean(ys_orig) for y in ys_orig]
# # # #     squared_error_regr = squared_error(ys_orig, ys_line)
# # # #     squared_error_y_mean = squared_error(ys_orig, y_mean_line)
# # # #     return 1 - (squared_error_regr/squared_error_y_mean)
    
# # # # m, b = best_fit_slope_and_intercept(xs,ys)
# # # # regression_line = [(m*x)+b for x in xs]

# # # # r_squared = coefficient_of_determination(ys,regression_line)
# # # # print(r_squared)

# # # # plt.scatter(xs,ys,color='#003F72',label='data')
# # # # plt.plot(xs, regression_line, label='regression line')
# # # # plt.legend(loc=4)
# # # # plt.show()

# record = { 
  
#  'Name' : ['Ankit', 'Swapnil', 'Aishwarya', 
#           'Priyanka', 'Shivangi', 'Shaurya' ],
    

#  'Stream' : ['Priyanka', 'Ankit', 'Science', 
#             'Math', 'Math', 'Shivangi'] } 
    
# create a dataframe 
# df = pd.DataFrame(record,
#                          columns = ['Name',  
#                                     'Stream']) 
# all=[]
# for c in df.columns:
#         filtered=df[df[c].str.lower().str.contains('priyanka')]
#         if(len(filtered)>0):
#             all.append(filtered)
# print(pd.concat(all).drop_duplicates().sort_index())
# # weekday=datetime.datetime.now().weekday()
# # dayname=calendar.day_name[weekday]
# # if (dayname !='Saturday' or dayname!='Sunday'):
# #     print (dayname)

# import requests
# import re

# # The target website
# url = "https://pouyanroohi.co/"

# # A list of payloads to test for SQL injection
# payloads = ["'", "\"", "AND 1=1", "OR 1=1"]

# # A regular expression to match common database errors
# error_regex = r"(SQL syntax|MySQL|database|syntax error)"

# # A loop that iterates over each payload
# for payload in payloads:
#     # Append the payload to the url as a query parameter
#     test_url = url + "?q=" + payload
    
#     # Send a GET request to the test_url
#     response = requests.get(test_url)
    
#     # Check if the response status code is 200 (OK)
#     if response.status_code == 200:
#         # Get the response content as text
#         content = response.text
        
#         # Search for database errors in the content using error_regex
#         match = re.search(error_regex, content, re.IGNORECASE)
        
#         # If there is a match, print a message indicating SQL injection vulnerability
#         if match:
#             print(f"SQL injection vulnerability found with payload: {payload}")
#             print(f"Error message: {match.group()}")
            
#         # Otherwise, print a message indicating no vulnerability found
#         else:
#             print(f"No vulnerability found with payload: {payload}")
            
#     # Otherwise, print an error message indicating request failure
#     else:
#         print(f"Request failed with status code: {response.status_code}")

# s=''
# arr=[5,8,9,0,66,18]
# for a in range(1,len(arr)):
#     if arr[a]%2==0 and arr[a-1] % 3 ==0:
#         s +=str(round(arr[a]/2))
#     else:
#         s +=str(round(arr[a] *2))

# print (s)

# import pandas as pd
# import mplfinance as mpf
# def pivot(df):
#     data = df.copy()
#     data['d1'] = data.high.shift(-1)
#     data['d2'] = data.high.shift(1)
#     data['d3'] = data.low.shift(-1)
#     data['d4'] = data.low.shift(1)
#     # find high pivots
#     cond_h = (data.high > data.d1) & (data.high > data.d2)
#     # find low pivots
#     cond_l = (data.low < data.d3) & (data.low < data.d4)
#     # mark pivots with 1 for high and -1 for low
#     data['pivots'] = 0
#     data.loc[cond_h,'pivots'] = 1
#     data.loc[cond_l,'pivots'] = -1
#     # return only the rows with pivots
#     return data[data.pivots != 0]
# # load the data
# #data = pd.read_csv("AAPL.csv", index_col=0, parse_dates=True)
# data=getTestData()
# # find the pivots

# print(data)
# import situations
# s1d=situations.Situation()
# s1d.above_sma_21_4h=True

# s4h=situations.Situation()
# s4h.above_sma_50_4h=True

# if s1d.above_sma_21_4h and s4h.above_sma_50_4h:
#     print ('yes')

#import modules

#import modules
# import numpy as np

# #define input arrays
# x = np.array([1, 2, 3, 4, 5, 6])
# y = np.array([2.1, 4.2, 3, 8.3, 18, 12])

# #calculate IQR for y values
# q1 = np.percentile(y, 35)
# q3 = np.percentile(y, 65)
# iqr = q3 - q1

# #set threshold for outliers
# threshold = 1 * iqr

# #filter out outliers
# x_clean = x[(y > q1 - threshold) & (y < q3 + threshold)]
# y_clean = y[(y > q1 - threshold) & (y < q3 + threshold)]

# #fit a line using numpy.polyfit
# coeffs = np.polyfit(x_clean, y_clean, deg=1)

# #print output
# print("Input x:", x)
# print("Input y:", y)
# print("Output x:", x_clean)
# print("Output y:", y_clean)
# print("Line coefficients:", coeffs)

# # # import numpy as np
# # # from scipy import stats

# # # def filter_outliers(x, y):
# # #     data = np.column_stack((x,y))
# # #     data_f = data[(np.abs(stats.zscore(data)) < 1).all(axis=1)]
# # #     x_f = data_f[:,0]
# # #     y_f = data_f[:,1]
# # #     return x_f, y_f

# # # def filter_outliers2(x, y):
# # #     data = np.column_stack((x,y))
    
# # #     # calculate IQR for each column
# # #     Q1 = np.quantile(data, 0.25, axis=0)
# # #     Q3 = np.quantile(data, 0.75, axis=0)
# # #     IQR = Q3 - Q1
    
# # #     # filter out outliers based on IQR
# # #     data_f = data[((data >= (Q1 - 1.5 * IQR)) & (data <= (Q3 + 1.5 * IQR))).all(axis=1)]
    
# # #     x_f = data_f[:,0]
# # #     y_f = data_f[:,1]
# # #     return x_f, y_f
# # # x = np.array([1, 2, 3, 4,5])
# # # y = np.array([2.1, 4.2, 8.3, 18,12])
# # # # y = np.array([0.4715, 0.4558, 0.4579, 0.4363])

# # # x_f,y_f=filter_outliers(x,y)
# # # print(x_f, y_f)


#import libraries
# # import numpy as np
# # import matplotlib.pyplot as plt

# # #define x and y arrays
# # x = [1, 2, 3, 4, 5]
# # y = [2.1, 4.2, 8.3, 18, 12]

# # #create a list of lists of 3 points from x and y arrays
# # points = [[(x[i], y[i]) for i in range(j,j+3)] for j in range(len(x)-2)]

# # #create an empty list to store slope, intercept, r-squared value, and list of 3 points as a tuple
# # results = []

# # #loop through each list of 3 points
# # for p in points:
# #     #extract x and y values from each point
# #     px = [q[0] for q in p]
# #     py = [q[1] for q in p]
# #     #find slope, intercept, and r-squared value of best fit line using np.polyfit function with degree=1 (linear)
# #     slope, intercept = np.polyfit(px ,py ,1)
# #     #calculate r-squared value using np.corrcoef function which returns a matrix of correlation coefficients 
# #     #and take the element at index (0 ,1) or (1 ,0) which is the same 
# #     r_squared = np.corrcoef(px ,py)[0 ,1]**2 
# #     #store slope ,intercept ,r-squared value ,and list of 3 points as a tuple in results list 
# #     results.append((slope ,intercept ,r_squared ,p))

# # #sort results list by r-squared value in descending order using sorted function with key=lambda x: x[2] (third element) 
# # #and reverse=True 
# # results = sorted(results ,key=lambda x: x[2] ,reverse=True)

# # #print results list 
# # print(results)

# # #plot each list of 3 points and their best fit line using plt.scatter and plt.plot functions 
# # for result in results:
# #     #unpack result tuple into slope ,intercept ,r_squared ,and p variables 
# #     slope ,intercept ,r_squared ,p = result 
# #     #extract x and y values from each point 
# #     px = [q[0] for q in p]
# #     py = [q[1] for q in p]
# #     #add points to plot using plt.scatter function with marker='o' (circle) 
# #     plt.scatter(px ,py ,marker='o')
# #     #add line of best fit to plot using plt.plot function with color='red' 
# #     plt.plot(px ,[slope*x + intercept for x in px] ,'red')
    
# # #show plot using plt.show function     
# # plt.show()

# # # # # import numpy as np
# # # # # import itertools
# # # # # # define a function to calculate r squared using numpy
# # # # # def r_squared(y1, y2):
# # # # #   # get the correlation matrix for y1 and y2
# # # # #   corr_matrix = np.corrcoef(y1,y2)
  
# # # # #   # slice the matrix with indexes [0,1] to get the value of R
# # # # #   R = corr_matrix[0][1]
  
# # # # #   # square the value of R to get R squared
# # # # #   return R**2
# # # # # def r2(comb):
# # # # #     xs = [x[0] for x in comb]    
# # # # #     ys = [y[1] for y in comb]    
# # # # #     coeff=np.polyfit(x=xs,y=ys,deg=1)
# # # # #     yn=np.poly1d(coeff)
# # # # #     r2 = r2_score(ys, yn(xs))
# # # # #     return r2

# # # # # x = [1, 2, 3, 4, 5]
# # # # # y = [12, 18, 8.3, 4.2, 2.1]
# # # # # # print(y)
# # # # # # points=[(1,2.1),(2,4.2),(3,8.3),(4,18),(5,12)]
# # # # # # concatenate x and y into one list
# # # # # points=list(zip(x,y))
# # # # # # get all combinations of 3 elements from z
# # # # # combs = list(itertools.combinations(points, 3))


# # # # # # sort the combinations by their r squared values in descending order
# # # # # sorted_combs = sorted(combs,key=lambda c: r2(c),reverse=True)

# # # # # # print the result
# # # # # print(sorted_combs[0])

# class MyClass:
#     def __init__(self):
#         self.my_variable = 10

#     def my_function(self):
#         print(self.my_variable)

# my_instance = MyClass()
# my_instance.my_function() # prints 10
# print(my_instance.my_variable) # prints 10
# from datetime import datetime

# df = pd.read_csv(f"https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1={datetime.now()-230*3600}&period2={datetime.now()}&interval=1h&events=history&includeAdjustedClose=true")
# print (df)

import pandas as pd
import numpy as np

df=getTestData()
def pivots(df, n):
    """
    This function finds pivots of a candlestick chart in a dataframe with high, low, close,
    open, and timestamp columns. The code finds pivots that are higher or lower from high/low
    of n candles left and right. The pivots are arranged in a way that after each high pivot,
    you see the low pivot and after a low pivot, you see a high pivot.
    """
    df['Pivot High'] = df.iloc[:, 1].rolling(window=n).max()
    df['Pivot Low'] = df.iloc[:, 2].rolling(window=n).min()
    df['Pivot High'].fillna(value=pd.Series(df['high'].rolling(window=n,
                        min_periods=1).max()), inplace=True)
    df['Pivot Low'].fillna(value=pd.Series(df['low'].rolling(window=n,
                        min_periods=1).min()), inplace=True)
    df['Pivot'] = np.nan
    condition = (df['high'] >= df['Pivot High'].shift(1)) & (df['high'] >= df['Pivot High'].shift(-1))
    df.loc[condition, 'Pivot'] = 'high'
    condition = (df['low'] <= df['Pivot Low'].shift(1)) & (df['low'] <= df['Pivot Low'].shift(-1))
    df.loc[condition, 'Pivot'] = 'low'
    return df[['timestamp', 'open', 'high', 'low', 'close', 'Pivot High', 'Pivot Low', 'Pivot']]
df2=(pivots(df,6))
print(df2.tail(20))


