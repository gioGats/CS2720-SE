class Item(object):
    """
    Item class stores relevant data from database
    """
    def __init__(self):
        self.id = 0
        self.price = 0

    def get_price(self):
        return self.price

    def set_price(self, price):
        self.price = price


class Cart(object):
    """
    Cart class stores items
    """
    def __init__(self):
        self.items = []
        self.item_counter = {}
        self.subtotal = 0
        self.salestax = 0.07
        self.total = 0

    def add_to_cart(self, item):
        self.items.append(item)
        if item._id in self._item_counter:
            self._item_counter[item.id] += 1
        else:
            self.item_counter[item._id] + 1
        self.subtotal += item.getPrice()
        self.total = self.subtotal * (1+self.salestax)

    def remove_from_cart(self, item):
        self.items.remove(item)

    def override_price(self, item, price):
        self.items[item].setPrice(price)

    def process_transaction(self):
        # Interate through items in cart
            # Add item to Sales table
            # Remove item from Inventory table
        # Add transaction to Transactions table
        return