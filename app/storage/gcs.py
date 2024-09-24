from google.cloud import storage # type: ignore
import os
from datetime import date
import uuid
import json
from app.core.config import get_settings

class GCStorage:
    def __init__(self):
        
        self.storage_client = storage.Client.from_service_account_info({
            "type": "service_account",
            "project_id": get_settings().security.service_account_project_id,
            "private_key_id": get_settings().security.service_account_private_key_id,
            "private_key": get_settings().security.service_account_private_key.get_secret_value(),
            "client_email": get_settings().security.service_account_client_email,
            "client_id": get_settings().security.service_account_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": get_settings().security.auth_provider_x509_cert_url,
            "client_x509_cert_url": get_settings().security.client_x509_cert_url
        })
        self.bucket_name = 'e-aluguel'
        self.date = str(date.today())
        self.unique_id = uuid.uuid4().hex

    def upload_file(self, file):
        bucket = self.storage_client.get_bucket(self.bucket_name)
        file_path = "aluguelapp/" + self.unique_id + (self.date)
        blob = bucket.blob(file_path)
        blob.upload_from_file(file.file, content_type='image/jpeg')
        return f'https://storage.googleapis.com/{self.bucket_name}/{file_path}'