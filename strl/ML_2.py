import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from  sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, KFold, train_test_split
from sklearn.ensemble import RandomForestClassifier 
from sklearn.neural_network import MLPClassifier

import GLOBAL , os
local=True
try:
    import subprocess
    interface = "eth0"
    ip = subprocess.check_output("ifconfig " + interface + " | awk '/inet / {print $2}'", shell=True).decode().strip()
    local = ip !=GLOBAL.SERVER_IP
except:
    local=True
def CalculateModels(exch,tf,symbol,target='buy'):
    rel_path = "Feature_Models/{}/{}/".format(exch,tf.lower())
    normalized_path=os.path.normcase(rel_path)
    abs_path = GLOBAL.ABSOLUTE(rel_path,local=local)

#    rel_path = "Feature_Models/{}/{}/{}_features_tp{}_cn{}.csv".format(exch,tf.lower(), symbol.upper(),tp,candles_forward)

    if not os.path.exists(abs_path): return []
    files = os.listdir(abs_path)

    matching_files = [os.path.join(abs_path, file) for file in files if file.startswith(f'{symbol.upper()}_features')]
    if not matching_files:return []
    matching_files = sorted(matching_files, key=lambda f: os.stat(f).st_ctime, reverse=True)

    my_path=(matching_files[0])
    fname=os.path.basename(my_path)
    tp_buy=fname.split('tpbuy_')[1].split('_')[0]
    tp_sell=fname.split('tpsell_')[1].split('_')[0]
    buys=fname.split('buys_')[1].split('_')[0]
    sells=fname.split('sells_')[1].split('_')[0]
    cn_buy=fname.split('cnbuy_')[1].split('_')[0]
    cn_sell=fname.split('cnsell_')[1].split('.')[0]
    df=pd.read_csv(my_path)
    tp=tp_buy
    total_deals=buys
    cn=cn_buy

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
    if target=='sell':
        y=y_sell
        cn=cn_sell
        tp=tp_sell
        total_deals=sells
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=101)
    rf0 = RandomForestClassifier()
    y_train=y_train.ravel()
    rf0.fit(X_train, y_train)

    ft_imp = pd.Series(rf0.feature_importances_, index=features.columns).sort_values(ascending=False)
    subset_features_index =ft_imp[ft_imp > 0.012].index
    X_imp=df[subset_features_index].values
    # X_train, X_test, y_train, y_test = train_test_split(X_imp, y, random_state=101)
    # rf = RandomForestClassifier()
    # y_train=y_train.ravel()
    # rf.fit(X_train, y_train)
    # print (f'Accuracy RF 0: {rf.score(X_test, y_test)}')
    # rf_y_pred = rf.predict(X_test)
    # print (f'Precision  RF 0:: {precision_score(y_test, rf_y_pred)}')
    # print (f'Recall  RF 0:: {recall_score(y_test, rf_y_pred)}')

    kf = KFold(n_splits=5, shuffle=True, random_state=10)
    # dt_accuracy_scores = []
    # dt_precision_scores = []
    # dt_recall_scores = []
    rf_accuracy_scores = []
    rf_precision_scores = []
    rf_recall_scores = []    
    # lr_accuracy_scores = []
    # lr_precision_scores = []
    # lr_recall_scores = []
    param_grid = {
    'max_depth': [5, 15, 25],
    'min_samples_leaf': [1, 3],
    'max_leaf_nodes': [10, 20, 35, 50]}
    #dt0 = DecisionTreeClassifier()
    #gs = GridSearchCV(dt0, param_grid, scoring='f1', cv=5)
    #gs.fit(X, y)    
    for train_index, test_index in kf.split(X_imp):
        X_train, X_test = X_imp[train_index], X_imp[test_index]
        y_train, y_test = y[train_index], y[test_index]
        #dt = DecisionTreeClassifier(max_depth=gs.best_params_['max_depth'], min_samples_leaf=gs.best_params_['min_samples_leaf'], max_leaf_nodes=gs.best_params_['max_leaf_nodes'])        
        # dt = DecisionTreeClassifier()
        # dt.fit(X_train, y_train)
        # dt_accuracy_scores.append(dt.score(X_test, y_test))
        # dt_y_pred = dt.predict(X_test)
        # dt_precision_scores.append(precision_score(y_test, dt_y_pred))
        # dt_recall_scores.append(recall_score(y_test, dt_y_pred))
        rf = RandomForestClassifier()
        y_train=y_train.ravel()
        rf.fit(X_train, y_train)
        rf_accuracy_scores.append(rf.score(X_test, y_test))
        rf_y_pred = rf.predict(X_test)
        rf_precision_scores.append(precision_score(y_test, rf_y_pred))
        rf_recall_scores.append(recall_score(y_test, rf_y_pred))

        # lr = LogisticRegression()
        # lr.fit(X_train, y_train)
        # lr_accuracy_scores.append(lr.score(X_test, y_test))
        # lr_y_pred = lr.predict(X_test)
        # lr_precision_scores.append(precision_score(y_test, lr_y_pred))
        # lr_recall_scores.append(recall_score(y_test, lr_y_pred))
    return [
             {"name":"Random Forest","model":rf,
             "cn":cn,"tp":tp,"deals":total_deals,
             "subset_features_index":subset_features_index,
             "accuracy_scores":rf_accuracy_scores,"precision_scores":rf_precision_scores,"recall_scores":rf_recall_scores}]
    print(f"Decision Tree on {symbol} with {target} target")
    print("  accuracy:", np.mean(dt_accuracy_scores))
    print("  precision:", np.mean(dt_precision_scores))
    print("  recall:", np.mean(dt_recall_scores))
    print(f"Logistic Regression on {symbol} with {target} target")
    print("  accuracy:", np.mean(lr_accuracy_scores))
    print("  precision:", np.mean(lr_precision_scores))
    print("  recall:", np.mean(lr_recall_scores))    
    
def Predict(input,exch='Kucoin',tf='4h',symbol='BTC_USDT',target='buy'):
    models=CalculateModels(exch=exch,tf=tf,symbol=symbol,target=target)

    for model in models:
        subset_features_index=model["subset_features_index"]
        subset_input = input[subset_features_index]
        subset_input_vals=subset_input.iloc[-1].values
        model["prediction"]=model["model"].predict([subset_input_vals])

    return models

#CalculateModels(exch='Kucoin',tf='1h',symbol='BNB_USDT',target='sell')
# tfs = ["1h"]
# symbols = ["BNB_USDT","TRX_USDT","FTM_USDT", "ADA_USDT", "MATIC_USDT", "BTC_USDT","ETH_USDT"]
# symbols = ["SOL_USDT","LTC_USDT","DOT_USDT", "BCH_USDT", "LINK_USDT", "UNI_USDT","FIL_USDT"]
# symbols = [ "ETH_USDT"]
# for tf in tfs:
#     for s in symbols:
#         for t in ["buy","sell"]:
#             models=CalculateModels(exch='Kucoin',tf=tf,symbol=s,target=t)
#             for m in models:
#                 print(f'Model: {m["name"]} - Symbol: {s}/{tf} -- target: {t} --- Precision: {round(np.mean(m["precision_scores"]),2)}')

