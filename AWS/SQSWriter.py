import boto3

class SQSWriter:

    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.sqs_client = boto3.client('sqs', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region)

    def write_message(self, queue_url:str, message_body:str) -> bool:

        # Send message to SQS queue
        try:
            self.sqs_client.send_message(
                QueueUrl=queue_url,
                DelaySeconds=1,
                MessageBody=message_body
            )
        except Exception as e:
            return False

        return True