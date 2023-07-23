import gc
from telegram import Update
from telegram.ext import CallbackContext

from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import analyzer as a
import situations as s
import analaysis_constants as ac
import pandas as pd
import ML_2
import numpy as np

def predict(tfs,exch,symbol,tf):
    analyzer=a.Analyzer()
    analyzer.init_data(tfs=tfs, symbol=symbol,exch=exch)
    sit=analyzer.situations[tf]
    sit_df=sit.short_term_df
    df0=sit_df[["close","open","high","low","volume"]].tail(1).reset_index(drop=True)
    features_dict=analyzer.features(tf=tf)
    df_features = pd.DataFrame.from_dict(features_dict,orient='columns').reset_index(drop=True)
    df_input=pd.concat([df0,df_features],axis=1)
    ################################################################## ML Prediction #############################################################################
    # lrow=df.iloc[-1]
    # f_input=[lrow.open,lrow.high,lrow.low,lrow.close,lrow.volume]
    # features_dict=analyzer.features(tf=tf)
    # df_features = pd.DataFrame.from_dict(features_dict,orient='columns')
    # df_features_row = df_features.iloc[0]

    # f_input.extend(df_features_row.values)
    predict={'buy':{1:'BUY',0:'Nothing'},
             'sell':{1:'SELL',0:'Nothing'}}
    
    text=''
    for target in ['buy','sell']:
        models=ML_2.Predict(input=df_input,exch=exch,tf=tf,symbol=symbol,target=f'{target}')
        if len(models)>0:
            for model in models:
                text +=(f'{model["name"]} for {target.capitalize()}: {predict[target][model["prediction"][0]]}') + '\r\n'
                text +=f'Current Candle: {sit_df.iloc[-1].time} (UTC)' + '\r\n'
                text +=(f'Total Deals: {model["deals"]} % , Candles: {model["cn"]} , TP: {model["tp"]}')+ '\r\n'
                # st.write(f'Min Recall Score:{round(np.min(model["recall_scores"]),2)}')
                text +=(f'Mean Recall Score:{round(np.mean(model["recall_scores"]),2)}')+ '\r\n'
                text +=(f'Mean Accuracy Score:{round(np.mean(model["accuracy_scores"]),2)}')+ '\r\n'
                text +=(f'Mean Precision Score:{round(np.mean(model["precision_scores"]),2)}')+ '\r\n'
                text +='--------------' +'\r\n'
    del analyzer
    del sit_df
    del sit
    del models
    gc.collect()
    return text
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
async def prd(update: Update, context: CallbackContext) -> None:
    tf=context.args[0]
    symbol = context.args[1]
    if not symbol.lower().__contains__('usdt') :symbol =f'{symbol}_usdt'
    text=predict(tfs=[tf],exch='Kucoin',symbol=symbol,tf=tf)
    await update.message.reply_text(text)


app = ApplicationBuilder().token("6256939846:AAFYhqqownIKVb5T-Bh5-r6ctwMmJWp_RfI").build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("predict", prd))

app.run_polling()
# predict(tfs=['4h'],symbol="btc_usdt",exch='Kucoin',tf='4h')
