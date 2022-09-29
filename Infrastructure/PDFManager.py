from fpdf import FPDF
import base64

class PDFManager:
    def __init__(self):
        pass

    def build_and_save_pdf(self, concert:str, number_of_tickets:int, transaction_id:str, email:str) -> str:
        
        # Build PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Courier','B',16)
        pdf.cell(40,10,'Concierto: '+concert)
        pdf.cell(40,10,'Número de entradas: '+number_of_tickets)
        pdf.cell(40,10,'Correo electrónico: '+email)
        pdf.cell(40,10,'ID de la transacción de compra: '+transaction_id)

        # Get PDF in base64 to be stored in DynamoDB
        pdf_bytes = pdf.output(transaction_id+'.pdf','S').encode('UTF-8')
        pdf_bytes_b64 = base64.b64encode(pdf_bytes)
        pdf_b64 = pdf_bytes_b64.decode('UTF-8')
        # TODO: this base64 returns a blank PDF, fix it
        #print(pdf_b64)

        # Save PDF in DynamoDB
        url = "string"

        # Return URL
        return url