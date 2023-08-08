import time
import websocket, json
import gzip, uuid
import config

socket = "wss://open-api-swap.bingx.com/swap-market"
socket="wss://open-api-ws.bingx.com/market"

# socket='wss://open-api-ws.bingx.com/market'
def on_ping(ws, message):
    print("Received ping:", message)
    ws.send('Pong')


def on_pong(ws, message):
    print("Received pong:", message)



def on_open(ws):
    print("opened")
    unique_id = str(uuid.uuid4())
    auth_data = {"id": unique_id, "reqType": "sub", "dataType": "DOT-USDT@kline_1min"}
    # auth_data={"id":unique_id,"reqType": "sub", "dataType":"ping"}
    # auth_data={"ping":"2177c68e4d0e45679965f482929b59c2","time":"2023-07-26T16:27:36.323+0800"}
    ws.send(json.dumps(auth_data))

def on_close(ws, close_status_code, close_msg):
    print("Connection closed:", close_status_code, close_msg)
def on_message(ws, message):
    try:
        decompressed_data = gzip.decompress(message)
        if decompressed_data==b'Ping':
            ws.send('Pong')
        else:
            json_data = json.loads(decompressed_data.decode("utf-8"))
            print(json_data)
    except Exception as e:
        print("Error",e)


def on_error(ws, error):
    print("Error:", error)
    # # Retry the connection after a delay
    # time.sleep(5)  # Adjust the delay as needed
    # print("Retrying...")
    # ws.run_forever()


ws = websocket.WebSocketApp(
    socket,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_ping=on_ping,
    on_pong=on_pong,
    on_close=on_close
    
)

ws.run_forever()
