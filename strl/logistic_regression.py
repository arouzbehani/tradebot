import pandas as pd
from sklearn.linear_model import LogisticRegression
from  sklearn.metrics import accuracy_score
import GLOBAL
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True
def Calculate(exch,tf,symbol,tp,candles_forward):
    rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(exch,tf, symbol,tp,candles_forward)
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    df=pd.read_csv(abs_path)
    column_numbers=range(0,len(df.columns)-2)
    features=(df.iloc[:,column_numbers])
    buy_targets=(df.iloc[:,[len(df.columns)-2]])
    sell_targets=(df.iloc[:,[len(df.columns)-1]])
    X=features.values
    y_buy=buy_targets.values
    y_sell=sell_targets.values
    model_buy=LogisticRegression(solver='liblinear')
    model_sell=LogisticRegression(solver='liblinear')
    model_buy.fit(X,y_buy)
    model_sell.fit(X,y_sell)
    
    print("prediction for datapoint buy 0:",model_buy.predict([X[0]]))
    print("buy Score:",model_buy.score(X,y_buy))
    y_pred_buy=model_buy.predict(X)
    accuracy_buy=accuracy_score(y_buy,y_pred_buy)
    print("Accuracy of Buy:",accuracy_buy)
    print("prediction for datapoint sell 0:",model_sell.predict([X[0]]))
    print("Sell Score:",model_buy.score(X,y_sell))
    y_pred_sell=model_sell.predict(X)
    accuracy_sell=accuracy_score(y_sell,y_pred_sell)
    print("Accuracy of Sell:",accuracy_sell)

Calculate('Kucoin','1d','FTM_USDT',5,7)