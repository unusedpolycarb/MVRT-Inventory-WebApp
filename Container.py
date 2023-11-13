class Container():
    name = ""
    contents = []
    is_checked = False

    def __init__(self, name):
        self.name = name
        self.contents = []
        self.is_checked = False

    def get_name(self):
        return self.name

    def get_num_shelves(self):
        return len(self.contents)

    def add(self, x):
        self.contents.append(x)

    def remove(self, component):
        self.contents.remove(component)

    def get_contents(self):
        return self.contents
