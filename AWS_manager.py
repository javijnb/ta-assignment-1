from dotenv import load_dotenv
import os
import boto3
import json
import time
import paramiko
import subprocess

# PATHS
SCRIPT_PATH = "./Scripts/"

# CREDENTIALS
load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
#INSTANCES_IDS = os.getenv('INSTANCES_IDS')
INSTANCES_IDS = ["i-0eeb6a2bed5a9f121"]
INSTANCES_DNS_NAMES = ["ec2-54-86-143-223.compute-1.amazonaws.com"]

# CLIENTS GLOBAL VARS
DYNAMODB_CLIENT = ""
EC2_CLIENT = ""
SQS_CLIENT = ""
S3_CLIENT = ""

# CLIENTS METHODS
def new_dynamoDB_client():
    dynamodb_client = boto3.client('dynamodb', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return dynamodb_client

def new_EC2_client():
    ec2_client = boto3.client('ec2', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return ec2_client

def new_SQS_client():
    sqs_client = boto3.client('sqs', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return sqs_client

def new_S3_client():
    s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_ACCESS_SECRET_KEY, region_name=AWS_REGION_NAME, aws_session_token=AWS_SESSION_TOKEN)
    return s3_client

# DYNAMODB INSTANCES
def create_dynamoDB_database():
    return

def delete_dynamoDB_database():
    return

# EC2 INSTANCES
def reboot_ec2_instances():
    print("<EC2> Reiniciando instancias...")
    EC2_CLIENT.reboot_instances(InstanceIds=INSTANCES_IDS)
    time.sleep(15)
    for index, instance_dns in enumerate(INSTANCES_DNS_NAMES):
        if index == len(INSTANCES_DNS_NAMES) - 1:
            print("<EC2> Deploying Frontend...")

            subprocess.call(['sh', SCRIPT_PATH+'zip_frontend.sh'])

            key = paramiko.RSAKey.from_private_key_file('./labsuser.pem')
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname=instance_dns, username='ec2-user', pkey=key, look_for_keys=False)

            sftp = ssh_client.open_sftp()
            sftp.put('./frontend.zip', '~/frontend.zip')
            sftp.put('deploy_frontend.sh', '~/deploy_frontend.sh')
            sftp.put(SCRIPT_PATH+'unzip_frontend.sh', '~/unzip_frontend.sh')
            sftp.close()

            ssh_client.exec_command('chmod +x unzip_frontend.sh')
            ssh_client.exec_command('./unzip_frontend.sh')
            ssh_client.exec_command('./deploy_frontend.sh')

            print("<EC2> Success deploying Frontend !")
    return

# SQS INSTANCES
def create_SQS_queue():
    return

def delete_SQS_queue():
    return

# S3 INSTANCES
def create_S3_instance():
    return

def delete_S3_instance():
    return

# MAIN
if __name__ == '__main__':

    print("Creando clientes AWS...")
    #DYNAMODB_CLIENT = new_dynamoDB_client()
    EC2_CLIENT = new_EC2_client()
    #S3_CLIENT = new_S3_client()
    #SQS_CLIENT = new_SQS_client()
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
            print("2) Eliminar una nueva instancia DynamoDB")
            response = int(input())
            if response == 1:
                create_dynamoDB_database()
            if response == 2:
                delete_dynamoDB_database()

        # S3
        elif user_input == 3:
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia S3")
            print("2) Eliminar una nueva instancia S3")
            response = int(input())
            if response == 1:
                create_S3_instance()
            if response == 2:
                delete_S3_instance()

        # SQS
        elif user_input == 4:
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia SQS")
            print("2) Eliminar una nueva instancia SQS")
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