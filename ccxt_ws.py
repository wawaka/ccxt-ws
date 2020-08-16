from pprint import pprint as pp
import time

import ccxt

import binance_ws


class binance_websocket(ccxt.binance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bws = None

    def fetch_order_book(self, symbol, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)
        symbol = market['id']

        if self.bws is None:
            self.bws = binance_ws.BinanceWebSocket()
            
        self.bws.ensure_opened()

        ob = self.bws.get_order_book(symbol, limit)

        if limit is not None:
            ob['asks'] = ob['asks'][:limit]
            ob['bids'] = ob['bids'][:limit]

        return {
            'asks': [[float(p), float(q)] for p, q in ob['asks']],
            'bids': [[float(p), float(q)] for p, q in ob['bids']],
            'nonce': ob['lastUpdateId'],
            'datetime': None,
            'timestamp': None,
        }



def test():
    binance = ccxt.binance()
    # order_book = binance.fetch_order_book("BTC/USDT", 5)
    pp(binance.fetch_order_book("BTC/USDT", 5))


def main():
    symbol = "BTC/USDT"
    # symbol = "BTCUSDT"
    # symbol = "btcusdt"
    binance = binance_websocket()
    # order_book = binance.fetch_order_book("BTC/USDT", 5)
    binance.fetch_order_book("BTC/USDT", 5)
    while True:
        time.sleep(30)
        ob = binance.fetch_order_book("BTC/USDT", 5)
        print(f"{len(ob['asks'])} {len(ob['bids'])}")
    # pp(binance.fetch_order_book("ETH/USDT", 5))
    # pp(binance.fetch_order_book("BTC/USDT", 5))
    # pp(binance.fetch_order_book("ETH/USDT", 5))
    # binance.load_markets()
    # self.load_markets()
    # market = binance.market(symbol)
    # pp(market)
    # request = {
    #     'symbol': market['id'],
    # }


if __name__ == "__main__":
    # test()
    main()
