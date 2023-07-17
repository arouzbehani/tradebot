import websocket
import json
import hmac
import hashlib
import time
import config
api_key = config.Kucoin_API_Key
api_secret = config.kucoin_API_Secret

# # # # # def on_message(ws, message):
# # # # #     data = json.loads(message)
# # # # #     if data['type'] == 'ticker':
# # # # #         print(data)

# # # # # def on_error(ws, error):
# # # # #     print(error)

# # # # # def on_close(ws):
# # # # #     print("### closed ###")

# # # # # def on_open(ws):
# # # # #     timestamp = str(int(time.time() * 1000))
# # # # #     str_to_sign = timestamp + 'GET' + '/api/v1/bullet-public'
# # # # #     signature = hmac.new(api_secret.encode(), str_to_sign.encode(), hashlib.sha256).hexdigest()
# # # # #     auth_payload = {
# # # # #         "id": "auth",
# # # # #         "type": "bullet-private",
# # # # #         "topic": "/market/ticker:BTC-USDT",
# # # # #         "auth": {
# # # # #             "apiKey": api_key,
# # # # #             "timestamp": timestamp,
# # # # #             "signature": signature
# # # # #         }
# # # # #     }
# # # # #     ws.send(json.dumps(auth_payload))

# # # # # if __name__ == "__main__":
# # # # #     websocket.enableTrace(True)
# # # # #     ws = websocket.WebSocketApp("wss://push-private.kucoin.com/endpoint",
# # # # #                                 on_message=on_message,
# # # # #                                 on_error=on_error,
# # # # #                                 on_close=on_close)
# # # # #     ws.on_open = on_open
# # # # #     ws.run_forever()


def on_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'ticker':
        print(data)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send(json.dumps({
        "id": "ticker",
        "type": "subscribe",
        "topic": "/market/ticker:BTC-USDT"
    }))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api/v1/bullet-public",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
