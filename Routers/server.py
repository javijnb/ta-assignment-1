from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import jwt
import os

from Infrastructure.CapacityChecker import CapacityChecker
from Infrastructure.PDFManager import PDFManager
from Infrastructure.TokenBuilder import TokenBuilder
from Infrastructure.UserAuthenticator import UserAuthenticator

from Models.AuthenticateRequestModel import AuthenticateRequestModel
from Models.AuthenticateResponseModel import AuthenticateResponseModel
from Models.PurchaseRequestModel import PurchaseRequestModel
from Models.PurchaseResponseModel import PurchaseResponseModel

app = FastAPI()
load_dotenv()

# Get ENV variables
PORT = os.getenv('PORT')
SECRET = os.getenv('SECRET')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_SECRET_KEY = os.getenv('AWS_ACCESS_SECRET_KEY')
AWS_REGION_NAME = os.getenv('AWS_REGION_NAME')
CAPACITY_QUEUE_URL = os.getenv('CAPACITY_QUEUE_URL')
USERS_TABLE_NAME = os.getenv('USERS_TABLE_NAME')
EVENTS_TABLE_NAME = os.getenv('EVENTS_TABLE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

@app.get("/purchase")
async def main(request: PurchaseRequestModel) -> PurchaseResponseModel:

    # Recogemos información de la request
    print("<PURCHASE> New request")
    requested_concert = request.concert
    requested_number_of_tickets = request.number_of_tickets
    transaction_id = request.transaction_id
    token = request.token

    try:
        decoded_jwt = jwt.decode(token, SECRET, algorithms=["HS256"])
        email = decoded_jwt["email"]

    except Exception as e:
        response:PurchaseResponseModel = PurchaseResponseModel(ticket_url="", transaction_id="", success=False, message="Purchase failed - Provided token was not valid")
        return response

    # Actualizar capacidad en caso de ser posible
    try:
        capacity_checker = CapacityChecker(EVENTS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME)
        capacity_operation_success = capacity_checker.update_capacity(event=requested_concert, number_of_tickets=requested_number_of_tickets)
        
        if not capacity_operation_success:
            response:PurchaseResponseModel = PurchaseResponseModel(ticket_url="", transaction_id="", success=False, message="Purchase failed - Requested event is full. There are no more tickets on sale")
            return response

        # Guardar el ticket
        # pdf_manager = PDFManager(AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME, S3_BUCKET_NAME)
        # ticket_url = pdf_manager.build_and_save_pdf(concert=requested_concert, number_of_tickets=requested_number_of_tickets, transaction_id=transaction_id, email=email)
        ticket_url = "ticket mock"

    except Exception as e:
        response:PurchaseResponseModel = PurchaseResponseModel(ticket_url="", transaction_id="", success=False, message="Purchase failed - "+str(e))
        return response

    # Enviar la URL en la respuesta
    response:PurchaseResponseModel = PurchaseResponseModel(ticket_url=ticket_url, transaction_id=transaction_id, success=True, message="Tickets purchased correctly")
    return response

    #TODO: devolver respuesta a la cola SQS


@app.post("/authenticate")
async def authenticate(request: AuthenticateRequestModel) -> AuthenticateResponseModel:
    
    # Recoger parámetros
    print("<AUTH> New request")
    email = request.email
    password = request.password

    # Consulto par (email, pwd) en el repositorio (DynamoDB)
    # user_authenticator = UserAuthenticator(USERS_TABLE_NAME, AWS_ACCESS_KEY, AWS_ACCESS_SECRET_KEY, AWS_REGION_NAME)
    # auth_success = user_authenticator.authenticate_user(email, password)
    auth_success = True

    # Si éxito, devolver token de sesión
    if auth_success:
        new_token:str = TokenBuilder.new_token(email=email, secret=SECRET)
        response:AuthenticateResponseModel = AuthenticateResponseModel(token=new_token, success=True)
        return response

    response:AuthenticateResponseModel = AuthenticateResponseModel(token="", success=False)
    return response