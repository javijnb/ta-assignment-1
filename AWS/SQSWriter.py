import boto3
    
sqs = boto3.client('sqs')

class SQSWriter:

    def write_message(self, queue_url:str, message_body:str) -> bool:

        # Send message to SQS queue
        try:
            sqs.send_message(
                QueueUrl=queue_url,
                DelaySeconds=1,
                MessageBody=message_body
            )
        except Exception as e:
            return False

        return True