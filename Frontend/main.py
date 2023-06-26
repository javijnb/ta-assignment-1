from flask import Flask, redirect, request, url_for
from flask import render_template
from dotenv import load_dotenv
import os
import boto3
import uuid

TOKEN = "app-token"

load_dotenv()

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

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            exist = DYNAMODB_CLIENT.scan(TableName = USERS_TABLE_NAME, ScanFilter = {
                    "email":{
                        "AttributeValueList":[ {"S": email} ],
                        "ComparisonOperator": "EQ"
                    },
                    "password":{
                        "AttributeValueList":[ {"S": password} ],
                        "ComparisonOperator": "EQ"
                    }})
            
            if len(exist['Items']) == 0:
                return render_template('login.html')
            
            else:
                try:
                    return redirect(url_for('home', email=email))

                except Exception as e:
                    print(str(e))

        except:
            return render_template('login.html')
        
    else:
        return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    email = request.args.get('email')
    backend_response = 0
    
    if request.method == 'POST':
        print("1")
        requested_tickets = request.form.get('requested_tickets')
        event = request.form.get('requested_event')

        if requested_tickets != '' and event != '':
            print("2")
            transaction_id = str(uuid.uuid1())
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
                        'StringValue': event,
                        'DataType': 'String'
                    },
                    'transaction_id': {
                        'StringValue': transaction_id,
                        'DataType': 'String'
                    },
                    'jwt': {
                        'StringValue': TOKEN,
                        'DataType': 'String'
                    }
                }, MessageDeduplicationId=transaction_id)
            
            backend_response = 0
            while backend_response == 0:
                print("3")
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
                            response_success = True
                            print("Exito")

                        elif response_type == 'error':
                            backend_response = 1
                            response_success = False

                    else:
                        SQS_CLIENT.change_message_visibility(QueueUrl=SQS_RESPONSE_QUEUE_URL, ReceiptHandle=res_receipt_handle, VisibilityTimeout=0)
                        backend_response = 0

            return render_template('home.html', events=get_eventos(), tickets=get_tickets(email), email=email)

    return render_template('home.html', events=get_eventos(), tickets=get_tickets(email), email=email)

def get_eventos():
    result = DYNAMODB_CLIENT.scan(TableName=EVENTS_TABLE_NAME)['Items']
    return result

def get_tickets(email:str):
    result = []
    tickets = DYNAMODB_CLIENT.scan(TableName=TICKETS_TABLE_NAME, ScanFilter= {
        'email':{
            'AttributeValueList':[{'S': email}],
            'ComparisonOperator': 'EQ'
        }
    })['Items']

    message = dict()

    for index, ticket in enumerate(tickets):
        sub_dict = {}
        sub_dict['StringValue'] = ticket
        sub_dict['DataType'] = 'String'
        url = S3_CLIENT.generate_presigned_url('get_object',
                                                Params={'Bucket': S3_BUCKET_NAME,
                                                       'Key': ticket['ticket_url']['S']},
                                                ExpiresIn=3600)
        sub_dict['potato_o_me_mato'] = url
        message[str(index)] = sub_dict

    #print(message)
    return message

# <!-- <li><a href="{{ url_for('download', url=tickets[clave].StringValue.ticket_url.S, correo=email) }}">{{tickets[clave].StringValue.ticket_url.S}}</a></li> -->
# @app.route('/download/<string:url>')
# def download(url):
#     correo = request.args.get('correo')
#     print(correo)
#     S3_CLIENT.download_file(S3_BUCKET_NAME, url, url)
#     return render_template('home.html', events=get_eventos(), tickets=get_tickets(correo), email=correo)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)