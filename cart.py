class Item(object):
    """
    Item class stores relevant data from database
    """
    def __init__(self):
        self._id = 0
        self._price = 0

    def get_price(self):
        return self._price

    def set_price(self, price):
        self._price = price


class Cart(object):
    """
    Cart class stores items
    """
    def __init__(self):
        self._items = []
        self._subtotal = 0
        self._salestax = 0.07
        self._total = 0

    def add_to_cart(self, item):
        self._items.append(item)
        self._subtotal += item.getPrice()
        self._total = self._subtotal * (1+self._salestax)

    def remove_from_cart(self, item):
        self._items.remove(item)

    def override_price(self, item, price):
        self._items[item].setPrice(price)

    def process_transaction(self):
        return
