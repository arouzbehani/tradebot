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
    analyzer.init_data(tfs=tfs,exch=exch,symbol=symbol,trend_limit_long=ac.Long_Term_Trend_Limit,trend_limit_short=ac.Short_Term_Trend_Limit
                       ,long_term_pivot_candles=ac.Long_Term_Candles,short_term_pivot_candles=ac.Short_Term_Candles,
                    pvt_trend_number=ac.Pivot_Trend_Number,waves_number=ac.PA_Power_Calc_Waves,candles_back=0,th=ac.Threshold/100)
    sit=analyzer.situations[tf]
    df=sit.long_term_df
    ################################################################## ML Prediction #############################################################################
    lrow=df.iloc[-1]
    f_input=[lrow.open,lrow.high,lrow.low,lrow.close,lrow.volume]
    features_dict=analyzer.features(tf=tf)
    df_features = pd.DataFrame.from_dict(features_dict,orient='columns')
    df_features_row = df_features.iloc[0]
    f_input.extend(df_features_row.values)
    predict={'buy':{1:'BUY',0:'Nothing'},
             'sell':{1:'SELL',0:'Nothing'}}
    
    text=''
    for target in ['buy','sell']:
        models=ML_2.Predict(input=f_input,exch=exch,tf=tf,symbol=symbol,target=f'{target}')
        if len(models)>0:
            for model in models:
                text +=(f'{model["name"]} for {target.capitalize()}: {predict[target][model["prediction"][0]]}') + '\r\n'
                text +=(f'Total Deals: {model["deals"]} % , Candles: {model["cn"]} , TP: {model["tp"]}')+ '\r\n'
                # st.write(f'Min Recall Score:{round(np.min(model["recall_scores"]),2)}')
                text +=(f'Mean Recall Score:{round(np.mean(model["recall_scores"]),2)}')+ '\r\n'
                text +=(f'Mean Accuracy Score:{round(np.mean(model["accuracy_scores"]),2)}')+ '\r\n'
                text +=(f'Mean Precision Score:{round(np.mean(model["precision_scores"]),2)}')+ '\r\n'
                text +='--------------' +'\r\n'
    del analyzer
    del df
    del sit
    del models
    gc.collect()
    return text
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
async def dt(update: Update, context: CallbackContext) -> None:
    tf=context.args[0]
    symbol = context.args[1]
    if not symbol.lower().__contains__('usdt') :symbol =f'{symbol}_usdt'
    text=predict(tfs=[tf],exch='Kucoin',symbol=symbol,tf=tf)
    await update.message.reply_text(text)


app = ApplicationBuilder().token("6256939846:AAFYhqqownIKVb5T-Bh5-r6ctwMmJWp_RfI").build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("dt", dt))

app.run_polling()
# predict(tfs=['4h'],symbol="btc_usdt",exch='Kucoin',tf='4h')
