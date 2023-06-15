from dotenv import load_dotenv
import os
import boto3

from Infrastructure.TokenBuilder import TokenBuilder
from Infrastructure.UserAuthenticator import UserAuthenticator
from Infrastructure.UUIDGenerator import UUIDGenerator

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
    logged = False

    while logged == False:

        try:
            fetched_request = SQS_CLIENT.receive_message(QueueUrl=SQS_REQUEST_QUEUE_URL, MessageAttributesNames=['All'], MaxNumberOfMessages=1)
            print("<NEW AUTH> Mensaje auth recibido")
            messages = list(fetched_request.keys())[0]

            if messages == 'Messages':
                attributes = fetched_request['Messages'][0]['MessagesAttributes']
                email = attributes['email']['StringValue']
                password = attributes['password']['StringValue']

                user_authenticator = UserAuthenticator(USERS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME)
                auth_response, auth_success = user_authenticator.authenticate_user(email, password)
            
                if auth_success:
                    new_token:str = TokenBuilder.new_token(email=email, secret=SECRET)
                    logged = True

        except Exception as e:
            print("<AUTH ERROR> Could not authenticate user: ", str(e))
            logged = False

    while True:

        try:
            # Coger mensaje:
            fetched_request = SQS_CLIENT.receive_message(QueueUrl=SQS_REQUEST_QUEUE_URL, MessageAttributesNames=['All'], MaxNumberOfMessages=1)
            print("<NEW REQ> Received new request")
            messages = list(fetched_request.keys())[0]

            if messages == 'Messages':
                req_receipt_handle = fetched_request['Messages'][0]['ReceiptHandle']
                
                # Si es compra, mandar solicitud y leer respuesta
                if fetched_request['Messages'][0]['Body'] == 'purchase':
                    SQS_CLIENT.delete_message(QueueUrl=SQS_REQUEST_QUEUE_URL, ReceiptHandle=req_receipt_handle)
                    print("<NEW PURCHASE>")
                    attributes = fetched_request['Messages'][0]['MessagesAttributes']
                    jwt_token = attributes['jwt']['StringValue']
                    email = attributes['email']['StringValue']
                    requested_event = attributes['event']['StringValue']
                    requested_tickets = attributes['tickets']['StringValue']
                    uuid_generator = UUIDGenerator()
                  
                    transaction_id = uuid_generator.new_uuid()

                elif True:
                    SQS_CLIENT.change_message_visibility(QueueUrl=SQS_REQUEST_QUEUE_URL, ReceiptHandle=req_receipt_handle, VisibilityTimeout=0)

                else:
                    print()

                attributes = fetched_request['Messages'][0]['MessagesAttributes']
                email = attributes['email']['StringValue']
                password = attributes['password']['StringValue']

            # Si es consulta de tickets, hacer aquí la consulta con DynamoDB

        except Exception as e:
            print("<ERROR> ", str(e))