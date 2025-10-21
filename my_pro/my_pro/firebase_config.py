import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your Firebase service account JSON file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
firebase_cred_path = os.path.join(BASE_DIR, 'eprojectpython.json')  # Put your JSON file here

cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()
