from pydantic import BaseModel

class AuthenticateRequestModel(BaseModel):
    email: str
    password: str