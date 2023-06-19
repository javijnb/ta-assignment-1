class UserAuthenticator:

    def __init__(self, users_dynamodb_table_name:str, aws_key:str, aws_secret_key:str, aws_region:str):
        self.users_dynamodb_table_name = users_dynamodb_table_name
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def authenticate_user(self, dynamodb_client, email:str, pwd:str):

        try:
            exist = dynamodb_client.scan(TableName = self.users_dynamodb_table_name,
                                ScanFilter = {
                                    "email":{
                                        "AttributeValueList":[ {"S": email} ],
                                        "ComparisonOperator": "EQ"
                                    },
                                    "password":{
                                        "AttributeValueList":[ {"S": pwd} ],
                                        "ComparisonOperator": "EQ"
                                    }})
            if len(exist['Items']) == 0:
                return 'error', False
            else:
                return 'success', True

        except Exception as e:
            raise e