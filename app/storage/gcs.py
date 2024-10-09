from google.cloud import storage # type: ignore
from datetime import date
import uuid

class GCStorage:
    def __init__(self, service_account_info: dict | None = None):
        self.storage_client = storage.Client.from_service_account_info(service_account_info)
        self.bucket_name = 'e-aluguel'
        self.date = str(date.today())
        self.unique_id = uuid.uuid4().hex

    def upload_file(self, file):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        file_path = "aluguelapp/" + self.unique_id + (self.date)
        blob = bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type='image/jpeg')
        return f'https://storage.googleapis.com/{self.bucket_name}/{file_path}'