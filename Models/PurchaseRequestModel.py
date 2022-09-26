from pydantic import BaseModel

class PurchaseRequestModel(BaseModel):
    concert: str
    number_of_tickets: int
    transaction_id: str
    token: str