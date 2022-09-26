from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import jwt
import os
from Infrastructure.TokenBuilder import TokenBuilder
from Infrastructure.UUIDGenerator import UUIDGenerator

from Models.AuthenticateRequestModel import AuthenticateRequestModel
from Models.AuthenticateResponseModel import AuthenticateResponseModel
from Models.PurchaseRequestModel import PurchaseRequestModel
from Models.PurchaseResponseModel import PurchaseResponseModel

app = FastAPI()
load_dotenv()
PORT = os.getenv('PORT')
SECRET = os.getenv('SECRET')

@app.get("/purchase")
async def main(request: PurchaseRequestModel) -> PurchaseResponseModel:
    concert = request.concert
    number_of_tickets = request.number_of_tickets
    transaction_id = request.transaction_id
    token = request.token

    try:
        jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        return {
            "message": e, 
            "success": "False"
        }

    # Comprobar capacidad
    # -> Error? Devolver mensaje de error
    # raise HTTPException(status_code=400, detail="Requested event is full. There are no more tickets on sale")

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