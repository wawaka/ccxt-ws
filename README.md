# modules
## order_book
Contains logic to maintain local order book
## binance_ws
contains class BinanceWebSocket which implements websocket-based order book maintenance for binance
## ccxt_ws
contains subclass with overloaded method fetch_order_book() which has same format as original but returns local order book (instantly)
## example
contains code to demonstrate that library is working

# limitations
## limit
This version is very loosely obeys limits argument and should be tuned according to real-life requirements
## params argument
not supported
## error handling
Does not handle network/websocket errors as it should be
## optimization
This version is optimized for order book updates. Different data structures might be required if number of data fetches is great.
## tests
No tests due to lack of time. order_book and binance_ws should be properly tested, including error handling scenarios. I prefer pytest.
## python package
not packaged as it should be due to lack of time. I hope this is not the goal of this challenge.