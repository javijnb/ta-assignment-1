import boto3

pdfs_folder = '../PDFs/'

class S3Connector:

    def __init__(self, aws_key:str, aws_secret_key:str, aws_region:str):
        self.aws_key = aws_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.s3_client = boto3.client('s3', aws_access_key_id=self.aws_key, aws_secret_access_key=self.aws_secret_key, region_name=self.aws_region)

    def save_new_item(self, bucket_name:str, filename:str) -> str:
        self.s3_client.Object(bucket_name, filename).put(Body=open(pdfs_folder + filename, 'rb'))
        url = "https://"+bucket_name+".s3."+self.aws_region+".amazonaws.com/"+filename
        return url

    def get_item(self, bucket_name:str, filename:str):
        self.s3_client.download_file(bucket_name, filename, filename)