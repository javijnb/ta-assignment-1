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
TICKETS_TABLE_NAME = os.getenv('TICKETS_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# AWS Clients
DYNAMODB_CLIENT = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
S3_CLIENT = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
SQS_CLIENT = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
SQS_REQUEST_QUEUE_NAME=os.getenv('SQS_REQUEST_QUEUE_NAME')
SQS_RESPONSE_QUEUE_NAME=os.getenv('SQS_RESPONSE_QUEUE_NAME')
SQS_REQUEST_QUEUE_URL=os.getenv('SQS_REQUEST_QUEUE_URL')
SQS_RESPONSE_QUEUE_URL=os.getenv('SQS_RESPONSE_QUEUE_URL')

SQS_REQUEST_QUEUE_URL = SQS_REQUEST_QUEUE_URL + SQS_REQUEST_QUEUE_NAME
SQS_RESPONSE_QUEUE_URL= SQS_RESPONSE_QUEUE_URL+ SQS_RESPONSE_QUEUE_NAME

while True:
    logged = False
    backend_response = 0

    while logged == False:

        try:
            print("<NEW AUTH>")
            print("<AUTH> Introduzca email: ")
            email = str(input())
            print("<AUTH> Introduca contraseña: ")
            password = str(input())

            user_authenticator = UserAuthenticator(USERS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME)
            auth_response, auth_success = user_authenticator.authenticate_user(DYNAMODB_CLIENT, email, password)
                
            if auth_success:
                new_token:str = TokenBuilder.new_token(email=email, secret=SECRET)
                logged = True

            else:
                print("<AUTH ERROR> Email y/o contraseña incorrectos")

        except Exception as e:
            print("<AUTH ERROR> Could not authenticate user: ", str(e))
            logged = False

    while True:

        try:
            # Elecciones:
            backend_response = 0
            print("¿Qué desea llevar a cabo?")
            print("1) Comprar")
            print("2) Consultar y descargar tickets")
            print("3) Salir")
            eleccion = str(input())

            # Compra
            if eleccion == '1':

                # Get eventos y datos
                result = DYNAMODB_CLIENT.scan(TableName=EVENTS_TABLE_NAME)['Items']
                print("<PURCHASE> Eventos disponibles: ", result)

                # Elegir tickets
                print("<PURCHASE> Elija nombre de evento: ")
                requested_event = str(input())
                print("<PURCHASE> Elija cuántos tickets desea comprar: ")
                requested_tickets = str(input())
                uuid_generator = UUIDGenerator()
                transaction_id = uuid_generator.new_uuid()

                # Mandar solicitud
                print(SQS_REQUEST_QUEUE_URL)
                SQS_CLIENT.send_message(QueueUrl=SQS_REQUEST_QUEUE_URL, MessageBody="backend-purchase", MessageGroupId="TA", MessageAttributes={
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
                    'jwt': {
                        'StringValue': new_token,
                        'DataType': 'String'
                    }
                }, MessageDeduplicationId=transaction_id)

                print("<PURCHASE> Petición enviada...")

                # Comprobar respuesta del backend
                while backend_response == 0:
                    print("Buscando respuesta")
                    message_response = SQS_CLIENT.receive_message(QueueUrl=SQS_RESPONSE_QUEUE_URL, MessageAttributeNames=['All'], MaxNumberOfMessages=1,)
                    message_list = list(message_response.keys())[0]

                    if message_list == 'Messages':
                        res_receipt_handle = message_response['Messages'][0]['ReceiptHandle']
                        response_email = message_response['Messages'][0]['MessageAttributes']['email']['StringValue']
                        response_transaction_id = message_response['Messages'][0]['MessageAttributes']['transaction_id']['StringValue']

                        if response_email == email and response_transaction_id == transaction_id:
                            
                            response_requested_tickets = message_response['Messages'][0]['MessageAttributes']['requested_tickets']['StringValue']
                            response_requested_event = message_response['Messages'][0]['MessageAttributes']['requested_event']['StringValue']
                            response_type = message_response['Messages'][0]['Body']

                            SQS_CLIENT.delete_message(QueueUrl=SQS_RESPONSE_QUEUE_URL, ReceiptHandle=res_receipt_handle)

                            if response_type == 'success':
                                backend_response = 1
                                response_ticket_url = message_response['Messages'][0]['MessageAttributes']['ticket_url']['StringValue']
                                print("<PURCHASE> Success: ", {
                                    'email': {
                                        'StringValue': response_email,
                                        'DataType': 'String'
                                    },
                                    'requested_tickets': {
                                        'StringValue': requested_tickets,
                                        'DataType': 'String'
                                    },
                                    'requested_event': {
                                        'StringValue': response_requested_event,
                                        'DataType': 'String'
                                    },
                                    'transaction_id': {
                                        'StringValue': transaction_id,
                                        'DataType': 'String'
                                    },
                                    'ticket_url': {
                                        'StringValue': response_ticket_url,
                                        'DataType': 'String'
                                    },
                                    'message': {
                                        'StringValue': 'Tickets purchased correctly',
                                        'DataType': 'String'
                                    }
                                })

                            elif response_type == 'error':
                                backend_response = 1
                                print("<PURCHASE> Error: ", {
                                    'email': {
                                        'StringValue': response_email,
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
                                    'message': {
                                        'StringValue': "Couldn't purchase tickets",
                                        'DataType': 'String'
                                    }
                                })

                        else:
                            SQS_CLIENT.change_message_visibility(QueueUrl=SQS_RESPONSE_QUEUE_URL, ReceiptHandle=res_receipt_handle, VisibilityTimeout=0)
                            backend_response = 0


            # Si es consulta de tickets, hacer aquí la consulta con DynamoDB
            elif eleccion == '2':
                print("<NEW CONSULT>")
                fetched_tickets = DYNAMODB_CLIENT.scan(TableName = TICKETS_TABLE_NAME,
                    ScanFilter = {
                        "email":{
                            "AttributeValueList":[ {"S": email} ],
                            "ComparisonOperator": "EQ"
                        }})['Items']
                    
                print("<CONSULT> Tickets recuperados! Disponibles:  (" + str(len(fetched_tickets)) + "):")

                # Devolver respuesta con lista de tickets
                message = {
                    'email': {
                        'StringValue': email,
                        'DataType': 'String'
                    },  
                }
                
                for index, ticket in enumerate(fetched_tickets):
                    sub_dict = {}
                    sub_dict['StringValue'] = ticket
                    sub_dict['DataType'] = 'String'
                    message[str(index)] = sub_dict
                    print(str(index) + ") Ticket - " + ticket['ticket_url']['S'])

                print("Elija el número del ticket que quiera descargar: ")
                order = str(input())
                ticket_url = message[order]['StringValue']['ticket_url']['S']
                ticket_name = ticket_url.split("/")[-1]
                print(ticket_name)
                S3_CLIENT.download_file(S3_BUCKET_NAME, ticket_name, ticket_name)

            else:
                print("<EXIT>")
                exit()

        except Exception as e:
            print("<ERROR> ", str(e))