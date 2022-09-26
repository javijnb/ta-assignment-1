from fastapi import FastAPI
from dotenv import load_dotenv
import jwt
import os

from Models.AuthenticateRequestModel import AuthenticateRequestModel
from Models.AuthenticateResponseModel import AuthenticateResponseModel
from Models.PurchaseRequestModel import PurchaseRequestModel
from Models.PurchaseResponseModel import PurchaseResponseModel

app = FastAPI()
load_dotenv()
PORT = os.getenv('PORT')
print(PORT)

@app.get("/purchase")
async def main(request: PurchaseRequestModel) -> PurchaseResponseModel:
    concert = request.concert
    number_of_tickets = request.number_of_tickets
    transaction_id = request.transaction_id
    token = request.token

    try:
        jwt.decode(token)
    except Exception:
        return {
            "message": "Provided token was not valid", 
            "success": "False"
        }

    response:PurchaseResponseModel = PurchaseResponseModel(ticket_url="url", transaction_id="12345")
    return response


@app.post("/authenticate")
async def authenticate(request: AuthenticateRequestModel) -> AuthenticateResponseModel:
    
    # Recoger parámetros
    email = request.email
    password = request.password

    # Consulto par (email, pwd) en el repositorio


    # Si éxito, devolver token de sesión
    if True:
        response:AuthenticateResponseModel = AuthenticateResponseModel(token="token", success=True)
        return response

    response:AuthenticateResponseModel = AuthenticateResponseModel(token="", success=False)
    return response