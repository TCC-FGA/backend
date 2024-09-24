from google.cloud import storage # type: ignore
import os
from datetime import date
import uuid
import json
from app.core.config import get_settings

class GCStorage:
    def __init__(self):

        self.storage_client = storage.Client.from_service_account_info(json.loads(get_settings().security.service_account.get_secret_value().strip("'")))
        self.bucket_name = 'e-aluguel'
        self.date = str(date.today())
        self.unique_id = uuid.uuid4().hex

    def upload_file(self, file):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        file_path = "aluguelapp/" + self.unique_id + (self.date)
        blob = bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type='image/jpeg')
        return f'https://storage.cloud.google.com/{self.bucket_name}/{file_path}'