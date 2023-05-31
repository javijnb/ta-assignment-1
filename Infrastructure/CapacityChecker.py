from fastapi import HTTPException
from AWS.DynamoDBConnector import DynamoDBConnector

class CapacityChecker:

    def __init__(self, events_dynamodb_table_name:str, aws_key:str, aws_secret_key:str, aws_region:str):
        self.events_dynamodb_table_name = events_dynamodb_table_name
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def update_capacity(self, event: str, number_of_tickets: int) -> bool:

        # Get current data from DynamoDB Events Table
        try:
            event_item = self.get_capacities(event)
        except Exception as e:
            raise e

        current_capacity = event_item["current_capacity"]
        max_capacity = event_item["max_capacity"]

        # Check if it is possible to purchase the amount of requested tickets
        if (number_of_tickets + current_capacity) > max_capacity:
            return False

        # Update capacity
        dynamodb_connector = DynamoDBConnector(self, self.aws_secret_key, self.aws_region)
        new_capacity = current_capacity + number_of_tickets
        result = dynamodb_connector.update_item(self.events_dynamodb_table_name, key='event_name', value=event, new_value=new_capacity)

        if not result.success:
            raise HTTPException(status_code=400, detail="Unable to update capacity of event <"+event+"> - "+result.message)
        
        return result.success


    def get_capacities(self, event:str) -> dict:

        # Get from DynamoDB repository max capacity for the requested event
        dynamodb_connector = DynamoDBConnector(self.aws_key, self.aws_secret_key, self.aws_region)
        try:
            event = dynamodb_connector.get_item(
                table_name= self.events_dynamodb_table_name,
                key="event", 
                type="S", 
                value=event
            )

            response = {
                "event": event["event"],
                "max_capacity": event["max_capacity"],
                "current_capacity": event["current_capacity"]
            }

            return response

        except Exception as e:
            raise e