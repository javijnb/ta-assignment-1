class CapacityChecker():

    def update_capacity(self, event: str, number_of_tickets: int) -> bool:

        # Si es posible, incrementa la capacidad del evento indicado en el número de tickets pasado por argumentos
        current_capacity = self.get_current_capacity(event=event)
        max_capacity = self.get_max_capacity(event=event)

        if (number_of_tickets + current_capacity) > max_capacity:
            return False
        
        # Update capacity with SQSWriter

    def get_current_capacity(self, event:str) -> int:

        # Get current capacity of the requested event with SQSReader
        print()

    def get_max_capacity(self, event:str) -> int:

        # Get from DynamoDB repository max capacity for the requested event with SQSReader
        print()