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

        ob = self.bws.get_order_book(symbol)

        if limit is not None:
            ob['asks'] = ob['asks'][:limit]
            ob['bids'] = ob['bids'][:limit]

        # convert to mimic original fetch_order_book() format
        return {
            'asks': [[float(p), float(q)] for p, q in ob['asks']],
            'bids': [[float(p), float(q)] for p, q in ob['bids']],
            'nonce': ob['lastUpdateId'],
            'datetime': None,
            'timestamp': None,
        }
