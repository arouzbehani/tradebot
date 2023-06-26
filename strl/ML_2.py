import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from  sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold, train_test_split
import GLOBAL , os
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True
def CalculateModels(exch,tf,symbol,tp,candles_forward,target='buy'):
    rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(exch,tf.lower(), symbol.upper(),tp,candles_forward)
    normalized_path=os.path.normcase(rel_path)
    abs_path = GLOBAL.ABSOLUTE(normalized_path,local=local)
    if not os.path.exists(abs_path): return []
    df=pd.read_csv(abs_path)
    cols_to_drop=[]
    if "timestamp" in df.columns:
        cols_to_drop.append('timestamp')
    if "time" in df.columns:
        cols_to_drop.append('time')
    df=df.drop(cols_to_drop,axis=1)
    column_numbers=range(0,len(df.columns)-2)
    features=(df.iloc[:,column_numbers])
    buy_targets=(df.iloc[:,[len(df.columns)-2]])
    sell_targets=(df.iloc[:,[len(df.columns)-1]])
    X=features.values
    y=buy_targets.values
    y_sell=sell_targets.values
    if target=='sell': y=y_sell
    kf = KFold(n_splits=5, shuffle=True, random_state=10)
    dt_accuracy_scores = []
    dt_precision_scores = []
    dt_recall_scores = []
    lr_accuracy_scores = []
    lr_precision_scores = []
    lr_recall_scores = []
    for train_index, test_index in kf.split(X):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        dt = DecisionTreeClassifier()
        dt.fit(X_train, y_train)
        dt_accuracy_scores.append(dt.score(X_test, y_test))
        dt_y_pred = dt.predict(X_test)
        dt_precision_scores.append(precision_score(y_test, dt_y_pred))
        dt_recall_scores.append(recall_score(y_test, dt_y_pred))
        lr = LogisticRegression()
        lr.fit(X_train, y_train)
        lr_accuracy_scores.append(lr.score(X_test, y_test))
        lr_y_pred = lr.predict(X_test)
        lr_precision_scores.append(precision_score(y_test, lr_y_pred))
        lr_recall_scores.append(recall_score(y_test, lr_y_pred))
    return [{"name":"Decision Tree","model":dt,"accuracy_scores":dt_accuracy_scores,"precision_scores":dt_precision_scores,"recall_scores":dt_recall_scores},
            {"name":"Logistic Regression","model":lr,"accuracy_scores":lr_accuracy_scores,"precision_scores":lr_precision_scores,"recall_scores":lr_recall_scores}]
    print(f"Decision Tree on {symbol} with {target} target")
    print("  accuracy:", np.mean(dt_accuracy_scores))
    print("  precision:", np.mean(dt_precision_scores))
    print("  recall:", np.mean(dt_recall_scores))
    print(f"Logistic Regression on {symbol} with {target} target")
    print("  accuracy:", np.mean(lr_accuracy_scores))
    print("  precision:", np.mean(lr_precision_scores))
    print("  recall:", np.mean(lr_recall_scores))    

def Predict(input,exch='Kucoin',tf='1d',symbol='BTC_USDT',tp=5,cn=7,target='buy'):
    models=CalculateModels(exch=exch,tf=tf,symbol=symbol,tp=tp,candles_forward=cn,target=target)

    for model in models:
        model["prediction"]=model["model"].predict([input])

    return models
# CalculateModels(exch='Kucoin',tf='4h',symbol='MATIC_USDT',tp=1.5,candles_forward=10,target='buy')