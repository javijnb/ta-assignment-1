from pydantic import BaseModel

class PurchaseResponseModel(BaseModel):
    ticket_url: str
    transaction_id: str
    success: bool
    message: str