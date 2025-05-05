import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIREBASE_CREDENTIAL_PATH = "credentials.json"
FIREBASE_STORAGE_BUCKET = "adi-file-uploaded"
GOOGLE_APPLICATION_CREDENTIALS = "credentials.json"
BIGQUERY_PROJECT_ID = ""
BIGQUERY_DATASET_ID = ""