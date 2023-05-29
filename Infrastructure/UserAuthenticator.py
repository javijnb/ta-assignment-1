from AWS.DynamoDBConnector import DynamoDBConnector

class UserAuthenticator:

    def __init__(self, users_dynamodb_table_name:str, aws_key:str, aws_secret_key:str, aws_region:str):
        self.users_dynamodb_table_name = users_dynamodb_table_name
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def authenticate_user(self, email:str, pwd:str):
        dynamodb_connector = DynamoDBConnector(self.aws_key, self.aws_secret_key, self.aws_region)
        success = dynamodb_connector.get_item(
            table_name= self.users_dynamodb_table_name,
            key="email", 
            type="S", 
            value=email
        )

        # TODO: check "success" content

        return success