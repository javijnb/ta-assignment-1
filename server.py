from dotenv import load_dotenv
import os
import boto3

from Infrastructure.CapacityChecker import CapacityChecker
from Infrastructure.PDFManager import PDFManager

load_dotenv()

# Get ENV variables
PORT = os.getenv('PORT')
SECRET = os.getenv('SECRET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')
EVENTS_TABLE_NAME = os.getenv('EVENTS_TABLE_NAME')
TICKETS_TABLE_NAME = os.getenv('TICKETS_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# AWS Clients
DYNAMODB_CLIENT = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
SQS_CLIENT = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
SQS_REQUEST_QUEUE_NAME=os.getenv('SQS_REQUEST_QUEUE_NAME')
SQS_RESPONSE_QUEUE_NAME=os.getenv('SQS_RESPONSE_QUEUE_NAME')
SQS_REQUEST_QUEUE_URL=os.getenv('SQS_REQUEST_QUEUE_URL')
SQS_RESPONSE_QUEUE_URL=os.getenv('SQS_RESPONSE_QUEUE_URL')

SQS_REQUEST_QUEUE_URL = SQS_REQUEST_QUEUE_URL + SQS_REQUEST_QUEUE_NAME
SQS_RESPONSE_QUEUE_URL= SQS_RESPONSE_QUEUE_URL+ SQS_RESPONSE_QUEUE_NAME

while True:

    print("Buscando respuesta")
    fetched_request = SQS_CLIENT.receive_message(QueueUrl=SQS_REQUEST_QUEUE_URL, MessageAttributeNames=['All'], MaxNumberOfMessages=1,)

    if list(fetched_request.keys())[0] == 'Messages':
        print(fetched_request)
        req_receipt_handle = fetched_request['Messages'][0]['ReceiptHandle']
        SQS_CLIENT.delete_message(QueueUrl=SQS_REQUEST_QUEUE_URL, ReceiptHandle=req_receipt_handle)

        if fetched_request['Messages'][0]['Body'] == 'backend-purchase':

            attributes = fetched_request['Messages'][0]['MessageAttributes']
            email = attributes['email']['StringValue']
            requested_tickets = attributes['requested_tickets']['StringValue']
            requested_event = attributes['requested_event']['StringValue']
            transaction_id = attributes['transaction_id']['StringValue']
            jwt_token = attributes['jwt']['StringValue']

            try:
                print("<PURCHASE> Handling ticket purchase...")

                # Actualizar capacidad en caso de ser posible
                capacity_checker = CapacityChecker(EVENTS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME, AWS_SESSION_TOKEN)
                capacity_operation_success = capacity_checker.update_capacity(event=requested_event, number_of_tickets=requested_tickets)
                
                if not capacity_operation_success:
                    print("<PURCHASE ERROR> Cannot purchase - Event "+requested_event+" is full")
                    SQS_CLIENT.send_message(QueueUrl=SQS_RESPONSE_QUEUE_URL, MessageBody="error", MessageGroupId="TA", MessageAttributes={
                        'email': {
                            'StringValue': email,
                            'DataType': 'String'
                        },
                        'requested_tickets': {
                            'StringValue': requested_tickets,
                            'DataType': 'String'
                        },
                        'requested_event': {
                            'StringValue': requested_event,
                            'DataType': 'String'
                        },
                        'transaction_id': {
                            'StringValue': transaction_id,
                            'DataType': 'String'
                        },
                        'error': {
                            'StringValue': 'Purchase failed - Requested event is full. There are no more tickets on sale',
                            'DataType': 'String'
                        }
                    }, MessageDeduplicationId=transaction_id)

                else:
                    # Guardar el ticket
                    pdf_manager = PDFManager(AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME, S3_BUCKET_NAME, AWS_SESSION_TOKEN)
                    ticket_url = pdf_manager.build_and_save_pdf(concert=requested_event, number_of_tickets=requested_tickets, transaction_id=transaction_id, email=email)

                    # Guardar entrada DynamoDB de pdf
                    DYNAMODB_CLIENT.put_item(TableName=TICKETS_TABLE_NAME, Item={
                        'email': {
                            'S': email
                        },
                        'ticket_url': {
                            'S': ticket_url
                        }
                    })

                    # Enviar la URL en la respuesta
                    print("<PURCHASE SUCCESS> Purchase of "+requested_tickets+" ticket for event "+requested_event+" was successful")
                    SQS_CLIENT.send_message(QueueUrl=SQS_RESPONSE_QUEUE_URL, MessageBody="success", MessageGroupId="TA", MessageAttributes={
                        'email': {
                            'StringValue': email,
                            'DataType': 'String'
                        },
                        'requested_tickets': {
                            'StringValue': requested_tickets,
                            'DataType': 'String'
                        },
                        'requested_event': {
                            'StringValue': requested_event,
                            'DataType': 'String'
                        },
                        'transaction_id': {
                            'StringValue': transaction_id,
                            'DataType': 'String'
                        },
                        'ticket_url': {
                            'StringValue': ticket_url,
                            'DataType': 'String'
                        },
                        'message': {
                            'StringValue': 'Tickets purchased correctly',
                            'DataType': 'String'
                        }
                    }, MessageDeduplicationId=transaction_id)

            except Exception as e:
                print("<ERROR> Unhandled error: ", e)
                SQS_CLIENT.send_message(QueueUrl=SQS_RESPONSE_QUEUE_URL, MessageBody="error", MessageGroupId="TA", MessageAttributes={
                    'email': {
                        'StringValue': email,
                        'DataType': 'String'
                    },
                    'requested_tickets': {
                        'StringValue': '0',
                        'DataType': 'String'
                    },
                    'requested_event': {
                        'StringValue': 'none',
                        'DataType': 'String'
                    },
                    'transaction_id': {
                        'StringValue': '0',
                        'DataType': 'String'
                    },
                    'error': {
                        'StringValue': str(e),
                        'DataType': 'String'
                    }
                })