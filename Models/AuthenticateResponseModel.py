from pydantic import BaseModel

class AuthenticateResponseModel(BaseModel):
    token: str
    success: bool