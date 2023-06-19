import boto3

class DynamoDBConnector:

    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str, aws_session_token:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.aws_session_token = aws_session_token
        self.dynamodb_client = boto3.client('dynamodb', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region, aws_session_token=self.aws_session_token)

    def save_new_item(self, table_name:str, item):
        self.dynamodb_client.put_item(TableName=table_name, Item=item)

    def get_item(self, table_name:str, key:str, type:str, value:str):
        result = self.dynamodb_client.scan(TableName = table_name, ScanFilter = {
            key:{
                "AttributeValueList":[ {type: value} ],
                "ComparisonOperator": "EQ"
            }})
        if len(result['Items']) == 0:
            return 0, False
        else:
            return result, True
    
    def update_item(self, table_name:str, value:str, new_value:str):
        try:
            response = self.dynamodb_client.update_item(
                TableName = table_name,
                Key = {
                    'event': {
                        'S': value
                    }
                },
                UpdateExpression = "SET current_capacity = :new_value",
                ExpressionAttributeValues={':new_value': {"S": str(new_value)}},
                ReturnValues="UPDATED_NEW")
            return {
                "message": response,
                "success": "True"
            }
            
        except Exception as e:
            return {
                "message": e, 
                "success": "False"
            }