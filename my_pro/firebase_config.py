from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

# Set base directory to current file's folder
BASE_DIR = Path(__file__).resolve().parent

# Load Firebase credentials
cred_path = BASE_DIR / "eprojectpython.json"

# Initialize Firebase app (if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# ✅ Test data to insert
data = {
    'name': 'Terminal User',
    'email': 'terminaluser@example.com',
    'role': 'tester',
    'age': 30
}

# Insert into 'User' collection
doc_ref = db.collection('User').add(data)

print("✅ Data inserted successfully into Firestore.")
