from Container import Container
class Part(Container):
    link = ""
    quantity = 0
    threshold = 0
    location = ""
    unit = ""

    def __init__(self, name, link, quantity, unit, threshold, location):
        self.name = name
        self.link = link
        self.quantity = quantity
        self.threshold = threshold
        self.location = location
        self.unit = unit

    def update_quantity(self, new_quantity):
        self.quantity = new_quantity

    def add_quantity(self):
        self.quantity+=1

    def subtract_quantity(self):
        self.quantity-=1

    def get_quantity(self):
        return self.quantity

    def get_status(self):
        return self.quantity > self.threshold

    def get_location(self):
        return self.location

    def get_unit(self):
        return self.unit

    def get_link(self):
        return self.link
