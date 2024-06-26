
import json
import websocket
import gzip
import io
URL="wss://open-api-ws.bingx.com/market" # replace a correct url you need in here 
CHANNEL= {"id":"24dd0e35-56a4-4f7a-af8a-394c7060909c","dataType":"BTC-USDT@kline_1min"} # this is just a demo channel, replace your topic you need in here 
class Feed(object):

    def __init__(self):
        self.url = URL 
        self.ws = None

    def on_open(self, ws):
        print('WebSocket connected')
        subStr = json.dumps(CHANNEL)
        ws.send(subStr)
        print("Subscribed to :",subStr)

    def on_data(self, ws, string, type, continue_flag):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(string), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        print(utf8_data)

    def on_message(self, ws, message):
        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(message), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')
        print(utf8_data)  #this is the message you need 
        if utf8_data == "Ping": # this is very important , if you receive 'Ping' you need to send 'Pong' 
           ws.send("Pong")

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print('The connection is closed!')

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            # on_data=self.on_data,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.ws.run_forever()


if __name__ == "__main__":
    feed = Feed()
    feed.start()