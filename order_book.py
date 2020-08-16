def update_order_book(dict_order_book, update):
    if update['u'] <= dict_order_book['lastUpdateId']:
        # update is already contained in this dict_order_book
        return
        
    if not update['U'] <= dict_order_book['lastUpdateId']+1 <= update['u']:
        raise Exception("incorrect order of updates for order book")

    update_order_dict(dict_order_book['asks'], update['a'])
    update_order_dict(dict_order_book['bids'], update['b'])
    dict_order_book['lastUpdateId'] = update['u']


def is_zero_quantity(quantity):
    return all([ch == '0' or not ch.isdigit() for ch in quantity])


def update_order_dict(order_dict, update_items):
    for price_level, quantity in update_items:
        if is_zero_quantity(quantity):
            try:
                del order_dict[price_level]
            except KeyError:
                pass # missing price levels for zero quantity is ok
        else:
            order_dict[price_level] = quantity


class OrderBook:
    def __init__(self):
        self.updates_buffer = []
        self.dict_order_book = None

    def update(self, update):
        if self.dict_order_book:
            self.update_order_book(update)
        else:
            self.updates_buffer.append(update)

    def update_order_book(self, update):
        update_order_book(self.dict_order_book, update)

    def add_snapshot(self, snapshot):
        if not self.updates_buffer:
            # do not apply snapshot with empty buffer - not possible to check if it can be merged
            return False

        dict_order_book = {
            "lastUpdateId": snapshot['lastUpdateId'],
            "asks": {p: q for p, q in snapshot['asks']},
            "bids": {p: q for p, q in snapshot['bids']},
        }
        try:
            for update in self.updates_buffer:
                update_order_book(dict_order_book, update)
        except Exception:
            # failed to apply updates to snapshot
            return False

        self.dict_order_book = dict_order_book
        self.updates_buffer = None
        return True

    def get_order_book(self):
        return {
            "lastUpdateId": self.dict_order_book['lastUpdateId'],
            "asks": sorted(self.dict_order_book['asks'].items()),
            "bids": sorted(self.dict_order_book['bids'].items(), reverse=True)
        }
