from fastapi import HTTPException

from AWS.SQSReader import SQSReader
from AWS.SQSWriter import SQSWriter
from AWS.DynamoDBConnector import DynamoDBConnector

class CapacityChecker:

    def __init__(self, capacity_queue_url:str, events_dynamodb_table_name:str, aws_key:str, aws_secret_key:str, aws_region:str):
        self.capacity_queue_url = capacity_queue_url
        self.events_dynamodb_table_name = events_dynamodb_table_name
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def update_capacity(self, event: str, number_of_tickets: int) -> bool:

        # Get current data in Capacity SQS Queue
        sqs_reader = SQSReader(self.aws_key, self.aws_secret_key, self.aws_region)
        message = sqs_reader.read_message(queue_url=self.capacity_queue_url)

        # Read capacity from JSON message
        for concert in message:
            if concert["event"] == event:
                current_capacity = concert["current_capacity"]
                break

        # Get max capacity for the requested event
        max_capacity = self.get_max_capacity(event=event)

        # Check if possible to purchase the amount of requested tickets
        if (number_of_tickets + current_capacity) > max_capacity:
            return False

        # Update the capacity
        for concert in message:
            if concert["event"] == event:
                concert["current_capacity"] += number_of_tickets

        # Send updated message with SQSWriter
        sqs_writer = SQSWriter(self.aws_key, self.aws_secret_key, self.aws_region)
        success = sqs_writer.write_message(queue_url=self.capacity_queue_url, message_body=message)
        if not success:
            raise HTTPException(status_code=400, detail="Unable to send message "+message+" to the SQS queue <"+self.capacity_queue_url+">")

        if current_capacity == None:
            raise HTTPException(status_code=400, detail="Unable to retrieve current capacity for requested event <"+event+">")
        
        return current_capacity


    def get_max_capacity(self, event:str) -> int:

        # Get from DynamoDB repository max capacity for the requested event with SQSReader
        dynamodb_connector = DynamoDBConnector(self.aws_key, self.aws_secret_key, self.aws_region)
        max_capacity = dynamodb_connector.get_item(
            table_name= self.events_dynamodb_table_name,
            key="event", 
            type="S", 
            value=event
        )
        return max_capacity