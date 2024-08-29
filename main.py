import sys
import os
import win32event
import win32api
import winerror
import firestore_file
from gui import main
from firestore_file import firestore_init
from device_id_logic import generate_and_save_uuid
from cache_logic import manage_device_cache
import globals
from multiprocessing import freeze_support


def prevent_multiple_instances():
    mutex_name = "MyUniqueApplicationMutex"
    mutex = win32event.CreateMutex(None, False, mutex_name)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        print("Another instance is already running. Exiting.")
        sys.exit(0)


if __name__ == "__main__":
    freeze_support()
    prevent_multiple_instances()

    print("Application starting...")
    device_id = generate_and_save_uuid()
    print(f"Device ID: {device_id}")

    globals.db = firestore_init()
    if globals.db is None:
        print("Failed to initialize Firestore. Exiting.")
        sys.exit(1)

    firestore_file.push_device_registry(device_id)
    manage_device_cache(device_id)

    print(f"Global accounts: {globals.tt_accounts}")
    print(f"Global proxies: {globals.proxies}")

    main()