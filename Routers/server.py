from fastapi import FastAPI
from dotenv import load_dotenv
import jwt
import os
import boto3

from Infrastructure.CapacityChecker import CapacityChecker
from Infrastructure.PDFManager import PDFManager
from Infrastructure.TokenBuilder import TokenBuilder
from Infrastructure.UserAuthenticator import UserAuthenticator

app = FastAPI()
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
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# AWS Clients
SQS_CLIENT = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
SQS_REQUEST_QUEUE_NAME=os.getenv('SQS_REQUEST_QUEUE_NAME')
SQS_RESPONSE_QUEUE_NAME=os.getenv('SQS_RESPONSE_QUEUE_NAME')
SQS_REQUEST_QUEUE_URL=os.getenv('SQS_REQUEST_QUEUE_URL')
SQS_RESPONSE_QUEUE_URL=os.getenv('SQS_RESPONSE_QUEUE_URL')

SQS_REQUEST_QUEUE_URL = SQS_REQUEST_QUEUE_URL + SQS_REQUEST_QUEUE_NAME
SQS_RESPONSE_QUEUE_URL= SQS_RESPONSE_QUEUE_URL+ SQS_RESPONSE_QUEUE_NAME

while True:

    fetched_request = SQS_CLIENT.receive_message(QueueUrl=SQS_REQUEST_QUEUE_URL, MessageAttributeNames=['All'], MaxNumberOfMessages=1)
    messages = list(fetched_request.keys())[0]
    print(messages)

    if messages == 'Messages':

        print("<NEW REQ> Mensaje recibido")
        req_receipt_handle = fetched_request['Messages'][0]['ReceiptHandle']
        SQS_CLIENT.delete_message(QueueUrl=SQS_REQUEST_QUEUE_URL, ReceiptHandle=req_receipt_handle)
        print("<NEW REQ> Mensaje eliminado")

        attributes = fetched_request['Messages'][0]['MessageAttributes']
        jwt_token = attributes['jwt']['StringValue']
        email = attributes['email']['StringValue']
        transaction_id = attributes['transaction_id']['StringValue']
        requested_event = attributes['event']['StringValue']
        requested_tickets = attributes['tickets']['StringValue']

        try:
            print("<PURCHASE> Handling ticket purchase...")
            decoded_jwt = jwt.decode(jwt_token, SECRET, algorithms=["HS256"])

            # Actualizar capacidad en caso de ser posible
            capacity_checker = CapacityChecker(EVENTS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME)
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
                })

            # Guardar el ticket
            pdf_manager = PDFManager(AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME, S3_BUCKET_NAME)
            ticket_url = pdf_manager.build_and_save_pdf(concert=requested_event, number_of_tickets=requested_tickets, transaction_id=transaction_id, email=email)
            ticket_url = "ticket url mocked"

            # Enviar la URL en la respuesta
            print("<PURCHASE SUCCESS> Purchase of "+requested_tickets+" for event "+requested_event+" was successful")
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
            })

        except Exception as e:
            print("<ERROR> Unhandled error: ", e)
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
                    'StringValue': str(e),
                    'DataType': 'String'
                }
            })