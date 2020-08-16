import json
import time
import threading
try:
    import thread
except ImportError:
    import _thread as thread
from pprint import pprint as pp

import websocket
import requests

import order_book


def fetch_order_book(symbol, limit=None):
    params = {
        'symbol': symbol
    }
    if limit is not None:
        params['limit'] = limit
    r = requests.get('https://www.binance.com/api/v3/depth', params)
    return r.json()


class LockedOrderBook:
    def __init__(self):
        self.book = order_book.OrderBook()
        self.user_lock = threading.Lock()
        self.internal_lock = threading.Lock()
        self.subscribe_sent = False
        self.ready = threading.Event()


class BinanceWebSocket:
    def __init__(self):
        self.order_books = {}
        self.order_books_lock = threading.Lock()
        self.subscriptions = []
        self.subscriptions_lock = threading.Lock()
        self.opened = threading.Event()
        self.ws = websocket.WebSocketApp(
            "wss://stream.binance.com:9443/ws",
            on_message = lambda ws, m: self.on_message(ws, m),
            on_error = lambda ws, e: self.on_error(ws, e),
            on_open = lambda ws: self.on_open(ws),
            on_close = lambda ws: self.on_close(ws)
        )
        thread.start_new_thread(self.run, ())

    def run(self):
        self.ws.run_forever()

    def on_message(self, ws, message):
        obj = json.loads(message)
        if 'id' in obj:
            with self.subscriptions_lock:
                try:
                    symbol = self.subscriptions[obj['id']]
                except IndexError:
                    raise Exception(f"unknown subscription {obj['id']}")

            if obj['result'] != None:
                raise Exception(f"failed subscription {symbol}")

            locked_order_book = self.get_locked_order_book(symbol)
            with locked_order_book.internal_lock, locked_order_book.user_lock:
                snapshot = fetch_order_book(symbol)
                if locked_order_book.book.add_snapshot(snapshot):
                    print(f"{symbol} ready")
                    locked_order_book.ready.set()

        elif 's' in obj:
            symbol = obj['s']
            locked_order_book = self.get_locked_order_book(symbol)
            with locked_order_book.internal_lock, locked_order_book.user_lock:
                locked_order_book.book.update(obj)
                snapshot = fetch_order_book(symbol)
                if locked_order_book.book.add_snapshot(snapshot):
                    print(f"{symbol} ready")
                    locked_order_book.ready.set()

    def on_error(self, ws, error):
        raise Exception(f"websocket error: {error}")
        # TODO: add proper error handling here

    def on_open(self, ws):
        self.opened.set()

    def on_close(self, ws):
        pass
        # TODO: here should go code to clear interanl state and restart socket again

    def ensure_opened(self):
        self.opened.wait()

    def get_locked_order_book(self, symbol):
        with self.order_books_lock:
            try:
                locked_order_book = self.order_books[symbol]
            except KeyError:
                locked_order_book = LockedOrderBook()
                self.order_books[symbol] = locked_order_book

        return locked_order_book

    def get_order_book(self, symbol):
        locked_order_book = self.get_locked_order_book(symbol)
        
        with locked_order_book.internal_lock:
            if not locked_order_book.subscribe_sent:
                with self.subscriptions_lock:
                    self.ws.send(json.dumps({
                        "method": "SUBSCRIBE",
                        "params": [
                            f"{symbol.lower()}@depth"
                        ],
                        "id": len(self.subscriptions),
                    }))
                    self.subscriptions.append(symbol)
                    locked_order_book.subscribe_sent = True

        locked_order_book.ready.wait()
        with locked_order_book.user_lock:
            return locked_order_book.book.get_order_book()
