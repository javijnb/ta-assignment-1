from dotenv import load_dotenv
import os
import boto3

load_dotenv()
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')

# TODO: Variables para ID_instancias y DNS_names

# CLIENTS
def new_dynamoDB_client():
    return

def new_EC2_client():
    return

def new_SQS_client():
    return

def new_S3_client():
    return

# DYNAMO_DB INSTANCES
def create_dynamoDB_database():
    return

def delete_dynamoDB_database():
    return

# EC2 INSTANCES
def create_EC2_frontend():
    return

def create_EC2_backend():
    return

# Reboot (?)
def delete_EC2_instance():
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
            print("¿Qué operación desea llevar a cabo?")
            print("1) Crear una nueva instancia EC2 de Backend")
            print("2) Crear una nueva instancia EC2 de Frontend")
            print("3) Eliminar una instancia EC2")
            response = int(input())
            if response == 1:
                create_EC2_backend()
            if response == 2:
                create_EC2_frontend()
            if response == 3:
                delete_EC2_instance()

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