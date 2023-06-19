from flask import Flask, redirect, request, url_for
from flask import render_template
from dotenv import load_dotenv
import os
import boto3

TOKEN = ""

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
                    #print(get_eventos)
                    return redirect(url_for('home', email=email))
                    #return render_template('home.html', data=get_eventos())

                except Exception as e:
                    print(str(e))

        except:
            return render_template('login.html')
        
    else:
        return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    email = "javijnb@gmail.com"
    return render_template('home.html', data=get_eventos(), tickets=get_tickets(email))

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

    message = {
        'email': {
            'StringValue': email,
            'DataType': 'String'
        },  
    }

    for index, ticket in enumerate(tickets):
        sub_dict = {}
        sub_dict['StringValue'] = ticket
        sub_dict['DataType'] = 'String'
        message[str(index)] = sub_dict
        print(str(index) + ") Ticket - " + ticket['ticket_url']['S'])

    return result

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)