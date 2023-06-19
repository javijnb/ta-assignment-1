from fastapi import HTTPException
from AWS.DynamoDBConnector import DynamoDBConnector

class CapacityChecker:

    def __init__(self, events_dynamodb_table_name:str, aws_key:str, aws_secret_key:str, aws_region:str, aws_session_token:str):
        self.events_dynamodb_table_name = events_dynamodb_table_name
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.aws_session_token = aws_session_token

    def update_capacity(self, event: str, number_of_tickets: int) -> bool:

        # Get current data from DynamoDB Events Table
        try:
            event_item = self.get_capacities(event)
        except Exception as e:
            raise e

        current_capacity = int(event_item["current_capacity"])
        max_capacity = int(event_item["max_capacity"])

        # Check if it is possible to purchase the amount of requested tickets
        print(type(number_of_tickets), type(current_capacity))
        suma = int(number_of_tickets) + int(current_capacity)
        if suma > max_capacity:
            print("<CapacityChecker> Capacidad sobrepasa el aforo máximo")
            return False

        # Update capacity
        print('<CapacityChecker> Purchasing...')
        dynamodb_connector = DynamoDBConnector(self.aws_key, self.aws_secret_key, self.aws_region, self.aws_session_token)
        result = dynamodb_connector.update_item(table_name=self.events_dynamodb_table_name, value=str(event), new_value=str(suma))

        if result['success'] == 'False':
            raise HTTPException(status_code=400, detail="Unable to update capacity of event <"+event+"> - "+result['message'])
        
        print("<CapacityChecker> Capacity OK")
        return result['success']

    def get_capacities(self, requested_event:str) -> dict:

        # Get from DynamoDB repository max capacity for the requested event
        dynamodb_connector = DynamoDBConnector(self.aws_key, self.aws_secret_key, self.aws_region, self.aws_session_token)
        try:
            event, success = dynamodb_connector.get_item(
                table_name= self.events_dynamodb_table_name,
                key="event", 
                type="S", 
                value=requested_event
            )

            print("<CapacityChecker> ", event, success)
            event = event['Items'][0]

            response = {
                "event": event["event"]['S'],
                "max_capacity": event["max_capacity"]['S'],
                "current_capacity": event["current_capacity"]['S']
            }

            return response

        except Exception as e:
            raise e