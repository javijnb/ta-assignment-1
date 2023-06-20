from dotenv import load_dotenv
import os
import boto3
import time
import paramiko

# PATHS
SCRIPT_PATH = "./Scripts/"

# CREDENTIALS
load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')

# AWS NAMES AND DNS
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')
EVENTS_TABLE_NAME = os.getenv('EVENTS_TABLE_NAME')
TICKETS_TABLE_NAME = os.getenv('TICKETS_TABLE_NAME')

SQS_REQUEST_QUEUE_NAME=os.getenv('SQS_REQUEST_QUEUE_NAME')
SQS_RESPONSE_QUEUE_NAME=os.getenv('SQS_RESPONSE_QUEUE_NAME')
SQS_REQUEST_QUEUE_URL=os.getenv('SQS_REQUEST_QUEUE_URL')
SQS_RESPONSE_QUEUE_URL=os.getenv('SQS_RESPONSE_QUEUE_URL')

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

INSTANCE_ID_0=os.getenv('INSTANCE_ID_0')
INSTANCE_ID_1=os.getenv('INSTANCE_ID_1')
INSTANCE_ID_2=os.getenv('INSTANCE_ID_2')
INSTANCE_DNS_0=os.getenv('INSTANCE_DNS_0')
INSTANCE_DNS_1=os.getenv('INSTANCE_DNS_1')
INSTANCE_DNS_2=os.getenv('INSTANCE_DNS_2')

INSTANCES_IDS = []
INSTANCES_IDS.append(INSTANCE_ID_0)
INSTANCES_IDS.append(INSTANCE_ID_1)
INSTANCES_IDS.append(INSTANCE_ID_2)

INSTANCES_DNS_NAMES = []
INSTANCES_DNS_NAMES.append(INSTANCE_DNS_0)
INSTANCES_DNS_NAMES.append(INSTANCE_DNS_1)
INSTANCES_DNS_NAMES.append(INSTANCE_DNS_2)

# CLIENTS GLOBAL VARS
DYNAMODB_CLIENT = ""
DYNAMODB_RESOURCE = ""
EC2_CLIENT = ""
SQS_CLIENT = ""
S3_CLIENT = ""
S3_RESOURCE = ""

# CLIENTS METHODS
def new_dynamoDB_client():
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return dynamodb_client, dynamodb_resource

def new_EC2_client():
    ec2_client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return ec2_client

def new_SQS_client():
    sqs_client = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return sqs_client

def new_S3_client():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    s3_resource = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return s3_client, s3_resource

# DYNAMODB INSTANCES
def create_dynamoDB_database():
    print("<DB> Creando bases de datos...")
    auth_table = DYNAMODB_RESOURCE.create_table(
        TableName=USERS_TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'email', 
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'email', 
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    auth_table.meta.client.get_waiter('table_exists').wait(TableName=USERS_TABLE_NAME)
    print("<DB> Tabla de autenticación creada con éxito")

    events_table = DYNAMODB_RESOURCE.create_table(
        TableName=EVENTS_TABLE_NAME,
        KeySchema=[{'AttributeName': 'event', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'event', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    events_table.meta.client.get_waiter('table_exists').wait(TableName=EVENTS_TABLE_NAME)
    print("<DB> Tabla de eventos creada con éxito")

    tickets_table = DYNAMODB_RESOURCE.create_table(
        TableName=TICKETS_TABLE_NAME,
        KeySchema=[{'AttributeName': 'email', 'KeyType': 'HASH'},
                   {'AttributeName': 'ticket_url', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'email', 'AttributeType': 'S'},
                              {'AttributeName': 'ticket_url', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )
    tickets_table.meta.client.get_waiter('table_exists').wait(TableName=TICKETS_TABLE_NAME)
    print("<DB> Tabla de tickets creada con éxito")

    DYNAMODB_CLIENT.put_item(TableName=USERS_TABLE_NAME, Item={'email':{'S': 'javijnb@gmail.com'}, 'password':{'S':'12345'}})
    DYNAMODB_CLIENT.put_item(TableName=USERS_TABLE_NAME, Item={'email':{'S': 'prueba@gmail.com'}, 'password':{'S':'prueba'}})
    DYNAMODB_CLIENT.put_item(TableName=EVENTS_TABLE_NAME, Item={'event':{'S': 'Avicii'}, 'max_capacity':{'S': '10'}, 'current_capacity':{'S': '0'}})
    DYNAMODB_CLIENT.put_item(TableName=EVENTS_TABLE_NAME, Item={'event':{'S': 'Måneskin'}, 'max_capacity':{'S': '10'}, 'current_capacity':{'S': '9'}})
    DYNAMODB_CLIENT.put_item(TableName=EVENTS_TABLE_NAME, Item={'event':{'S': 'Red Hot CHilli Peppers'}, 'max_capacity':{'S': '10'}, 'current_capacity':{'S': '10'}})
    DYNAMODB_CLIENT.put_item(TableName=TICKETS_TABLE_NAME, Item={'email':{'S': 'javijnb@gmail.com'}, 'ticket_url':{'S':'www.google.es'}})
    print("<DB> Tablas pobladas y creadas con éxito!")
    return

def delete_dynamoDB_database():
    print("<DB> Eliminando tablas de la instancia de DynamoDB...")
    DYNAMODB_CLIENT.delete_table(TableName=USERS_TABLE_NAME)
    DYNAMODB_CLIENT.delete_table(TableName=EVENTS_TABLE_NAME)
    DYNAMODB_CLIENT.delete_table(TableName=TICKETS_TABLE_NAME)
    print("<DB> Tablas eliminadas con éxito!")
    return

# EC2 INSTANCES
def reboot_ec2_instances():
    print("<EC2> Reiniciando instancias...")
    EC2_CLIENT.reboot_instances(InstanceIds=INSTANCES_IDS)
    time.sleep(8)
    for index, instance_dns in enumerate(INSTANCES_DNS_NAMES):
        if index == len(INSTANCES_DNS_NAMES) - 1:

            print("<EC2> Conectando con la instancia ["+instance_dns+"]...")
            key = paramiko.RSAKey.from_private_key_file('./labsuser.pem')
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=instance_dns, username='ec2-user', pkey=key, look_for_keys=False)

            print("<EC2> Enviando Frontend...")
            sftp = ssh_client.open_sftp()
            sftp.put('./frontend.zip', '/home/ec2-user/frontend.zip')
            sftp.put('./Scripts/deploy_frontend.sh', '/home/ec2-user/deploy_frontend.sh')
            sftp.put('./Scripts/unzip_frontend.sh', '/home/ec2-user/unzip_frontend.sh')
            sftp.close()
            print("<EC2> Desplegando Frontend...")
            ssh_client.exec_command('chmod +x *.sh')
            ssh_client.exec_command('./unzip_frontend.sh')
            print("<EC2> Success deploying Frontend !")

            # print("<EC2> Enviando Client...")
            # sftp = ssh_client.open_sftp()
            # sftp.put('./client.zip', '/home/ec2-user/client.zip')
            # sftp.put('./Scripts/deploy_client.sh', '/home/ec2-user/deploy_client.sh')
            # sftp.put('./Scripts/unzip_client.sh', '/home/ec2-user/unzip_client.sh')
            # sftp.close()
            # print("<EC2> Desplegando Client...")
            # ssh_client.exec_command('chmod +x *.sh')
            # ssh_client.exec_command('./unzip_client.sh')
            # print("<EC2> Success deploying Client !")

        else:
            print("<EC2> Conectando con la instancia ["+instance_dns+"]...")
            key = paramiko.RSAKey.from_private_key_file('./labsuser.pem')
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=instance_dns, username='ec2-user', pkey=key, look_for_keys=False)

            print("<EC2> Enviando Backend ["+str(index)+"]...")
            sftp = ssh_client.open_sftp()
            sftp.put('./backend.zip', '/home/ec2-user/backend.zip')
            sftp.put('./Scripts/deploy_backend.sh', '/home/ec2-user/deploy_backend.sh')
            sftp.put('./Scripts/unzip_backend.sh', '/home/ec2-user/unzip_backend.sh')
            sftp.close()

            print("<EC2> Desplegando Backend ["+str(index)+"]...")
            ssh_client.exec_command('chmod +x *.sh')
            ssh_client.exec_command('./unzip_backend.sh')

            print("<EC2> Success deploying Backend ["+str(index)+"] !")

    return

# SQS INSTANCES
def create_SQS_queue():
    print("<SQS> Creando colas SQS Request y Response ...")
    SQS_CLIENT.create_queue(QueueName=SQS_REQUEST_QUEUE_NAME, Attributes={'VisibilityTimeout':'10', 'FifoQueue': 'true', 'ContentBasedDeduplication': 'false', 'MessageRetentionPeriod': '3600'})
    SQS_CLIENT.create_queue(QueueName=SQS_RESPONSE_QUEUE_NAME, Attributes={'VisibilityTimeout':'10', 'FifoQueue': 'true', 'ContentBasedDeduplication': 'false', 'MessageRetentionPeriod': '3600'})
    print("<SQS> Colas creadas con éxito!")
    return

def delete_SQS_queue():
    print("<SQS> Eliminando colas...")
    SQS_CLIENT.delete_queue(QueueUrl=SQS_REQUEST_QUEUE_URL+SQS_REQUEST_QUEUE_NAME)
    SQS_CLIENT.delete_queue(QueueUrl=SQS_RESPONSE_QUEUE_URL+SQS_RESPONSE_QUEUE_NAME)
    print("<SQS> Colas eliminadas con éxito!")
    return

# S3 INSTANCES
def create_S3_instance():
    print("<S3> Creando repositorio S3 de PDFs...")
    S3_CLIENT.create_bucket(Bucket=S3_BUCKET_NAME)
    print("<S3> Bucket creado con éxito!")
    return

def delete_S3_instance():
    print("<S3> Eliminando repositorio S3...")
    bucket_object = S3_RESOURCE.Bucket(S3_BUCKET_NAME)
    bucket_object.objects.all().delete()
    bucket_object.delete()
    print("<S3> Repositorio eliminado con éxito!")
    return

# MAIN
if __name__ == '__main__':

    print("Creando clientes AWS...")
    DYNAMODB_CLIENT, DYNAMODB_RESOURCE = new_dynamoDB_client()
    EC2_CLIENT = new_EC2_client()
    S3_CLIENT, S3_RESOURCE = new_S3_client()
    SQS_CLIENT = new_SQS_client()
    print("Clientes AWS creados con éxito!\n")

    while True:
        print("Elige qué tipo de servicio desea gestionar:")
        print("1) EC2")
        print("2) DynamoDB")
        print("3) S3")
        print("4) SQS")
        print("5) Salir")
        user_input = int(input())

        # EC2
        if user_input == 1:
            reboot_ec2_instances()

        # DynamoDB
        elif user_input == 2:
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia DynamoDB")
            print("2) Eliminar una instancia DynamoDB")
            response = int(input())
            if response == 1:
                create_dynamoDB_database()
            if response == 2:
                delete_dynamoDB_database()

        # S3
        elif user_input == 3:
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia S3")
            print("2) Eliminar una instancia S3")
            response = int(input())
            if response == 1:
                create_S3_instance()
            if response == 2:
                delete_S3_instance()

        # SQS
        elif user_input == 4:
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia SQS")
            print("2) Eliminar una instancia SQS")
            response = int(input())
            if response == 1:
                create_SQS_queue()
            if response == 2:
                delete_SQS_queue()

        elif user_input == 5:
            raise SystemExit

        else:
            print("Por favor seleccione una opción válida")

        print("\n-------------------------------------------------------------------\n")