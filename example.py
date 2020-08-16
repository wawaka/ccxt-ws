import ccxt
import ccxt_ws

from pprint import pprint as pp


def test():
    binance = ccxt.binance()
    pp(binance.fetch_order_book("BTC/USDT", 5))


def main():
    binance = ccxt_ws.binance_websocket()
    pp(binance.fetch_order_book("BTC/USDT", 5))
    pp(binance.fetch_order_book("ETH/USDT", 5))
    pp(binance.fetch_order_book("BTC/USDT", 5))
    pp(binance.fetch_order_book("ETH/USDT", 5))


if __name__ == "__main__":
    test()
    main()
