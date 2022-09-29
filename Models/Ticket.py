class Ticket:
    def __init__(self, transaction_id:str, pdf_b64:str):
        self.transaction_id = transaction_id
        self.pdf_b64 = pdf_b64