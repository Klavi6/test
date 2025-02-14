class Container:
    def __init__(self, capacity):
        self.capacity = capacity
        self.level = 0
    
    def get(self, amount):
        self.level += amount
