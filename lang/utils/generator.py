class Generator:
    def __init__(self, items):
        self.items = items
        self.count = len(self.items)
        self.pointer = 0

    def peek(self, offset=0):
        if not self.has_next(): return None
        return self.items[self.pointer + offset]

    def next(self, offset = 1): 
        self.pointer += offset
        return self.peek()
    
    def has_next(self): 
        return self.pointer < self.count