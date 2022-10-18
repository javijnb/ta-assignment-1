import boto3

class DynamoDBConnector:

    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.dynamodb_client = boto3.client('dynamodb', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region)

    def save_new_item(self, table_name:str, item):
        self.dynamodb_client.put_item(TableName=table_name, Item=item)

    def get_item(self, table_name:str, key:str, type:str, value:str):
        response = self.dynamodb_client.get_item(
            TableName=table_name, 
            Key={
                key: {
                    type: value
                }
            }
        )
        return response["Item"]