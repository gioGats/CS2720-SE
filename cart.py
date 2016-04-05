class Item(object):
    """
    Item class stores relevant data from database
    """
    def __init__(self, item_id):
        # TODO Link correctly to inventory and product databases
        db_list = inventory.get_item(item_id)
        self.item_id = db_list[0]
        self.product_id = db_list[1]
        self.item_type = db_list[2]
        self.price = products.get_price(self.product)

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
        self.product_counter = {}
        self.subtotal = 0
        self.salestax = 0.07
        self.total = 0

    def add_to_cart(self, item):
        self.items.append(item)
        if item._id in self._item_counter:
            self._item_counter[item.id] += 1
        else:
            self.item_counter[item._id] + 1
        self.subtotal += item.get_price()
        self.total = self.subtotal * (1+self.salestax)

    def remove_from_cart(self, item):
        self.subtotal -= item.get_price()
        self.items.remove(item)
        self.total = self.subtotal * (1+self.salestax)

    def override_price(self, item, price):
        self.items[item].setPrice(price)

    def override_tax(self, tax):
        self.salestax = tax

    def process_cart(self, transaction_id):
        for item in self.items:
            # TODO Fix new sale syntax
            sales(item.item_id, item.get_price(), transaction_id)
            # TODO Remove from inventory table
        return


class Transaction(object):
    def __init__(self, name, contact):
        self.cust_name = name
        self.cust_contact = contact
        self.cart = Cart()

    def process_transaction(self, payment_type):
        # TODO Fix new transaction syntax
        transactions(self.cust_name, self.cust_contact, payment_type)
        # TODO Get transaction id
        transaction_id = 0
        self.cart.process_cart(transaction_id)