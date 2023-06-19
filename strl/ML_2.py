import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from  sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold, train_test_split
import GLOBAL
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True
def Calculate(exch,tf,symbol,tp,candles_forward,target='buy'):
    rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(exch,tf, symbol,tp,candles_forward)
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)
    df=pd.read_csv(abs_path)
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
    print(f"Decision Tree on {symbol} with {target} target")
    print("  accuracy:", np.mean(dt_accuracy_scores))
    print("  precision:", np.mean(dt_precision_scores))
    print("  recall:", np.mean(dt_recall_scores))
    print(f"Logistic Regression on {symbol} with {target} target")
    print("  accuracy:", np.mean(lr_accuracy_scores))
    print("  precision:", np.mean(lr_precision_scores))
    print("  recall:", np.mean(lr_recall_scores))    
    # model_buy=LogisticRegression(solver='liblinear')
    # model_sell=LogisticRegression(solver='liblinear')
    # model_buy.fit(X,y_buy)
    # model_sell.fit(X,y_sell)
    
    # print("prediction for datapoint buy 0:",model_buy.predict([X[0]]))
    # print("buy Score:",model_buy.score(X,y_buy))
    # y_pred_buy=model_buy.predict(X)
    # accuracy_buy=accuracy_score(y_buy,y_pred_buy)
    # print("Accuracy of Buy:",accuracy_buy)
    # print("prediction for datapoint sell 0:",model_sell.predict([X[0]]))
    # print("Sell Score:",model_buy.score(X,y_sell))
    # y_pred_sell=model_sell.predict(X)
    # accuracy_sell=accuracy_score(y_sell,y_pred_sell)
    # print("Accuracy of Sell:",accuracy_sell)


    # X_train, X_test_buy, y_train_buy, y_test_buy = train_test_split(X, y_buy, random_state=22)
    # model_tree_buy=DecisionTreeClassifier()
    # model_tree_buy.fit(X_train,y_train_buy)
    # print("Decision Tree Buy Predict at 0:",model_tree_buy.predict([X[0]]))
    # X_train, X_test_sell, y_train_sell, y_test_sell = train_test_split(X, y_sell, random_state=22)
    # model_tree_sell=DecisionTreeClassifier()
    # model_tree_sell.fit(X_train,y_train_sell)
    # print("Decision Tree sell Predict at 0:",model_tree_sell.predict([X[0]]))
    # y_pred_tree_buy=model_tree_buy.predict(X_test_buy)
    # print ("precision_score on Buy Test Data:",precision_score(y_test_buy,y_pred_tree_buy))
    # print ("recall on Buy Test Data:",recall_score(y_test_buy,y_pred_tree_buy))

    # y_pred_tree_sell=model_tree_sell.predict(X_test_sell)
    # print ("precision_score on Sell Test Data:",precision_score(y_test_sell,y_pred_tree_sell))
    # print ("recall on Sell Test Data:",recall_score(y_test_sell,y_pred_tree_sell))
symbols=['BTC_USDT','FTM_USDT']
targets=['buy','sell']
for symbol in symbols:
    for target in targets:
        Calculate('Kucoin','1d',symbol,5,7,target)