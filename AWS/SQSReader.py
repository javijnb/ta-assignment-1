import boto3

class SQSReader:

    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.sqs_client = boto3.client('sqs', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region)

    def read_message(self, queue_url:str) -> str:

        # Leer mensaje de la cola especificada
        response = self.sqs_client.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=0
        )

        message = response['Messages'][0]['Body']

        # Para eliminar el mensaje, obtener el campo 'ReceiptHandle'
        receipt_handle = message['ReceiptHandle']
        self.sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        return message