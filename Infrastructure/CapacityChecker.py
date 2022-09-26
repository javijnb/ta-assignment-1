from fastapi import HTTPException

from Infrastructure.SQSReader import SQSReader
from Infrastructure.SQSWriter import SQSWriter

class CapacityChecker:

    def __init__(self, capacity_queue_url:str):
        self.capacity_queue_url = capacity_queue_url

    def update_capacity(self, event: str, number_of_tickets: int) -> bool:

        # Get current data in Capacity SQS Queue
        sqs_reader = SQSReader()
        message = sqs_reader.read_message(queue_url=self.capacity_queue_url)

        # Read capacity from JSON message
        for concert in message:
            if concert["event"] == event:
                current_capacity = concert["current_capacity"]
                break

        # Get max capacity for the requested event
        max_capacity = self.get_max_capacity(event=event)

        # CHeck if possible to purchase the amount of requested tickets
        if (number_of_tickets + current_capacity) > max_capacity:
            return False

        # Update the capacity
        for concert in message:
            if concert["event"] == event:
                concert["current_capacity"] += number_of_tickets

        # Send updated message with SQSWriter
        sqs_writer = SQSWriter()
        success = sqs_writer.write(queue_url=self.capacity_queue_url, message_body=message)
        if not success:
            raise HTTPException(status_code=400, detail="Unable to send message "+message+" to the SQS queue <"+self.capacity_queue_url+">")

        if current_capacity == None:
            raise HTTPException(status_code=400, detail="Unable to retrieve current capacity for requested event <"+event+">")
        
        return current_capacity


    def get_max_capacity(self, event:str) -> int:

        # Get from DynamoDB repository max capacity for the requested event with SQSReader
        print()