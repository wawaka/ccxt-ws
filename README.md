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
Does not handle network/websocket errors as it should be. Socket restart is not performed on close/error. The code should clean internal structures and restart.
## optimization
This version is optimized for order book updates. Different data structures might be required if number of data fetches is great.
## tests
No tests due to lack of time. order_book and binance_ws should be properly tested, including error handling scenarios. I prefer pytest.
## python package
Not packaged as it should be due to lack of time. I hope this is not the goal of this challenge.

# scalability/availability
fetch_order_book(): the data served to users can be just static json files updated periodically by another services. Files can be stored in a cloud service and served by a bunch of 'server' services just reading static files from cloud storage and returning it to users
We will have files named according to the original scheme: https://www.binance.com/api/v3/depth?symbol=ETHUSDT&limit=5
 with 2 variables - symbol and limit.
How to update those files: there will be a number of instances of 'updater' service which keep websocket connection open and maintains local order book. after each update it forms static files (by symbol and limit) and sends them to cloud storage (paying attention to lastUpdateId so recently updated files will not be overwritten by older ones). If any of updater instances goes down - others will continue to generate updates. This redundancy of updater services will grant us tolerance to failures.