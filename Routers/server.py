from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import jwt
import os
from Infrastructure.CapacityChecker import CapacityChecker
from Infrastructure.TokenBuilder import TokenBuilder
from Infrastructure.UUIDGenerator import UUIDGenerator

from Models.AuthenticateRequestModel import AuthenticateRequestModel
from Models.AuthenticateResponseModel import AuthenticateResponseModel
from Models.PurchaseRequestModel import PurchaseRequestModel
from Models.PurchaseResponseModel import PurchaseResponseModel

app = FastAPI()
load_dotenv()

# Get ENV variables
PORT = os.getenv('PORT')
SECRET = os.getenv('SECRET')
CAPACITY_QUEUE_URL = os.getenv('CAPACITY_QUEUE_URL')

@app.get("/purchase")
async def main(request: PurchaseRequestModel) -> PurchaseResponseModel:
    requested_concert = request.concert
    requested_number_of_tickets = request.number_of_tickets
    transaction_id = request.transaction_id
    token = request.token

    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        return {
            "message": e, 
            "success": "False"
        }

    # Actualizar capacidad en caso de ser posible
    capacity_checker = CapacityChecker(CAPACITY_QUEUE_URL)
    capacity_operation_success = capacity_checker.update_capacity(event=requested_concert, number_of_tickets=requested_number_of_tickets)
    if not capacity_operation_success:
        raise HTTPException(status_code=400, detail="Requested event is full. There are no more tickets on sale")

    # Guardar el ticket
    # -> Error? Devolver mensaje de error
    # raise HTTPException(status_code=500, detail="Could not store ticket in the AWS Repository")


    # Enviar la URL en la respuesta
    response:PurchaseResponseModel = PurchaseResponseModel(ticket_url="url", transaction_id=transaction_id)
    return response


@app.post("/authenticate")
async def authenticate(request: AuthenticateRequestModel) -> AuthenticateResponseModel:
    
    # Recoger parámetros
    email = request.email
    password = request.password

    # Consulto par (email, pwd) en el repositorio


    # Si éxito, devolver token de sesión
    if True:
        new_token:str = TokenBuilder.new_token(SECRET)
        response:AuthenticateResponseModel = AuthenticateResponseModel(token=new_token, success=True)
        return response

    response:AuthenticateResponseModel = AuthenticateResponseModel(token="", success=False)
    return response