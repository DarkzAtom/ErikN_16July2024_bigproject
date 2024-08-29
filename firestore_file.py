import os
import sys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import globals


def get_credentials_path():
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in a normal Python environment
        base_path = os.path.dirname(os.path.abspath(__file__))

    cred_path = os.path.join(base_path, "dbkey", "eriknbigproject-firebase-adminsdk-mddgp-16b8b2b316.json")
    print(f"Credentials path: {cred_path}")
    print(f"Credentials file exists: {os.path.exists(cred_path)}")
    return cred_path


def firestore_init():
    try:
        if not firebase_admin._apps:
            cred_path = get_credentials_path()
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        print("Firestore initialized successfully.")
        return db
    except Exception as e:
        print(f"Error initializing Firestore: {e}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        return None


def push_device_registry(device_id):
    try:
        db = firestore_init()
        if db is None:
            print("Firestore initialization failed. Cannot push device registry.")
            return

        doc_ref = db.collection('devices_registry').document(f'{device_id}')
        doc = doc_ref.get()
        if doc.exists:
            print(f"Device {device_id} already registered.")
            return
        else:
            doc_ref.set({'up_to_date': False})
            print(f"Device {device_id} registered successfully.")
    except Exception as e:
        print(f'Error in push_device_registry, device_id = {device_id}: {e}')


# Add this for testing
if __name__ == "__main__":
    push_device_registry("test_device_id")
    input("Press Enter to exit...")