from fastapi import FastAPI

from Models.AuthenticateRequestModel import AuthenticateRequestModel
from Models.AuthenticateResponseModel import AuthenticateResponseModel

app = FastAPI()

@app.get("/")
async def main():
    return {"message": "Hello World"}

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