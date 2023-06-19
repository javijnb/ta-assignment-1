from flask import Flask, request
from flask import render_template
import requests
import json
import os
import boto3

# Comunicación mediante colas (!)
backend_url = "http://localhost:8000/authenticate"
TOKEN = ""

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
def index():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        payload = {'email': email, 'password': password}
        response = requests.post(backend_url, json=payload)
        
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json["success"] == True:
                TOKEN = response_json["token"]
                return "Página de compra"
            
        return 'Error en el inicio de sesión'

    return render_template('index.html')


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

    for ticket in tickets:
        dictionary = dict()
        item_ticket = ticket['pdf']['S'].split("/")[-1]
        url = S3_CLIENT.generate_presigned_url('get_object', Params={
            'Bucket': S3_BUCKET_NAME,
            'Key': item_ticket
        }, ExpiresIn=7200)
        dictionary['ticket_name'] = item_ticket
        dictionary['url'] = url
        result.append(dictionary)

    return result


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)