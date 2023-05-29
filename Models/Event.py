class Event:
    def __init__(self, event_name:str, max_capacity: int, current_capacity: int = 0):
        self.event_name = event_name
        self.max_capacity = max_capacity
        self.current_capacity = current_capacity