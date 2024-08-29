import json
import os
import sys

import globals
from PyQt5.QtWidgets import QMessageBox, QApplication

# Указываем пути к JSON-файлам
TTACCOUNTS_JSON_PATH = 'accounts_cache.json'
PROXIES_JSON_PATH = 'proxies_cache.json'

def show_critical_message(message):
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "No Data Error!", f"{message}")
    sys.exit(0)


def manage_device_cache(device_id):
    if not os.path.exists(TTACCOUNTS_JSON_PATH):
        dict_to_append = {}
        docs_ref = globals.db.collection('tiktok_accounts_list').stream()
        for doc in docs_ref:
            dict_to_append[doc.id] = doc.to_dict()
        with open(TTACCOUNTS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(dict_to_append, file, indent=4)
    if not os.path.exists(PROXIES_JSON_PATH):
        dict_to_append = {}
        docs_ref = globals.db.collection('proxieslist').stream()
        for doc in docs_ref:
            dict_to_append[doc.id] = doc.to_dict()
        with open(PROXIES_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(dict_to_append, file, indent=4)
    check_update_flag_docref = globals.db.collection('devices_registry').document(f'{device_id}')
    cuf_doc = check_update_flag_docref.get()
    flag = cuf_doc.get('up_to_date')
    if not flag:
        dict_to_append = {}
        docs_ref = globals.db.collection('tiktok_accounts_list').stream()
        for doc in docs_ref:
            dict_to_append[doc.id] = doc.to_dict()
        with open(TTACCOUNTS_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(dict_to_append, file, indent=4)
        dict_to_append = {}
        docs_ref = globals.db.collection('proxieslist').stream()
        for doc in docs_ref:
            dict_to_append[doc.id] = doc.to_dict()
        with open(PROXIES_JSON_PATH, 'w', encoding='utf-8') as file:
            json.dump(dict_to_append, file, indent=4)


    tt_accounts = {}
    proxies = {}

    with open(TTACCOUNTS_JSON_PATH, 'r', encoding='utf-8') as file:
        tt_accounts = json.load(file)
    with open(PROXIES_JSON_PATH, 'r', encoding='utf-8') as file:
        proxies = json.load(file)

    if not tt_accounts or not proxies:
        show_critical_message("The data on accounts or proxies is not available!\nThis might be due to the network issues. Please, check your internet connection and try to run the program again.\nIf the issue persists, please inform the administrator.")

    device_ref = globals.db.collection('devices_registry').document(f"{device_id}")
    device_ref.update({
        'up_to_date': True
    })

    globals.tt_accounts = tt_accounts
    globals.proxies = proxies



