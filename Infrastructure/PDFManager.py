from fpdf import FPDF
from AWS.S3Connector import S3Connector

pdfs_folder = "../PDFs/"

class PDFManager:
    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str, bucket_name:str, aws_session_token:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.aws_session_token = aws_session_token
        self.bucket_name = bucket_name

    def build_and_save_pdf(self, concert:str, number_of_tickets:int, transaction_id:str, email:str) -> str:
        
        # Build PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Courier','B',11)
        pdf.cell(40,10,'Concierto: '+concert, ln=1)
        pdf.cell(40,10,'Número de entradas: '+number_of_tickets, ln=2)
        pdf.cell(40,10,'Correo electrónico: '+email, ln=3)
        pdf.cell(40,10,'ID de la transacción de compra: '+transaction_id, ln=4)

        # Create PDF
        filename = transaction_id+'.pdf'
        pdf.output(str(filename),'F')

        # Save PDF in S3
        s3_connector = S3Connector(self.aws_key, self.aws_secret_key, self.aws_region, self.aws_session_token)
        url = s3_connector.save_new_item(self.bucket_name, filename)
        return url