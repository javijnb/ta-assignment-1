import boto3

sqs = boto3.client("sqs")

class SQSReader:

    def read_message(self, queue_url:str) -> str:

        # Leer mensaje de la cola especificada
        response = sqs.receive_message(
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
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        return message