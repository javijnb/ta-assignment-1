import boto3

dynamodb_client = boto3.client('dynamodb', aws_access_key_id="AWS_ACCESS_KEY_ID", aws_secret_access_key="TU_AWS_SECRET_ACCESS_KEY", region_name="TU_REGION_NAME")

class DynamoDBConnector:

    def __init__(self):
        pass

    def save_new_item(self, table_name:str, item):
        dynamodb_client.put_item(TableName=table_name, Item=item)

    def get_item(self, table_name:str, key:str, type:str, value:str):
        response = dynamodb_client.get_item(
            TableName=table_name, 
            Key={
                key: {
                    type: value
                }
            }
        )
        return response["Item"]