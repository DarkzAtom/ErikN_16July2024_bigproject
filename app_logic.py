import random
from PyQt5.QtWidgets import QMessageBox
import time
import globals
import firestore_file
from tt_automation import main as tt_automation


def init_tiktok_scrape(task, account, proxy, username, post_link, likes):
    print('prinial init tt scrape')
    local_db = firestore_file.firestore_init()
    print('zafetchil local db ')

    print('inittt: norm schtialo acc and prox')
    try:
        print("ALL PASSED accs:")
        for acc in account:
            print(acc)
        print(f"ALL PASSED proxies:")
        for prox in proxy:
            print(prox)
        # rand_time = random.randint(1, 4)
        time.sleep(20)
        # time.sleep(rand_time)
        print(f"username: {username}")
        print(f"post_link: {post_link}")
        print(f"likes: {likes}")
        tt_automation(account, proxy, username, post_link, likes)
        free_usage_accnproxy_db(local_db, account, proxy)
        success = True
    except Exception as e:
        print(f"EXCEPTION IN INIT__TT__SCRAPE: {e}")
        free_usage_accnproxy_db(local_db, account, proxy)
        success = False
        return task, success, account, proxy

    return task, success, account, proxy


def get_proxy(self, db, passed_number):
    if passed_number == 0:
        return []
    try:
        proxies_list = []
        doc_ref = db.collection("inuse").document("proxy_inuse_status")
        proxy_dict = doc_ref.get().to_dict()
        print(f"THE NUMBER OF OVERALL AVAILABLE PROXIES: {len(proxy_dict)*5}")
        while True:
            for i in range(0, 5):
                for j in range(0, len(proxy_dict)):
                    if proxy_dict[f'{str(j+1).zfill(5)}']['inuse'][f'{i+1}'] == True:
                        continue
                    else:
                        proxy_address_dict = {
                            'id': str(j+1).zfill(5),
                            'round': i+1
                        }
                        proxies_list.append(proxy_address_dict)
                    if len(proxies_list) >= passed_number:
                        break
                if len(proxies_list) >= passed_number:
                    break
            break

        random.shuffle(proxies_list)
        print(f'fetched proxies in the get_proxy(): {proxies_list}')
        update_dict = {}

        for proxy_address_dict in proxies_list:
            key = f"{proxy_address_dict['id']}.inuse.{proxy_address_dict['round']}"
            update_dict[key] = True

        print(f"final dict to update in get_proxy(): {update_dict}")

        try:
            doc_ref.update(update_dict)
            return proxies_list
        except Exception as e:
            print(f"error updating document IN GET PROXY: {e}")
            return False

    except Exception as e:
        print(f"exception in get_proxy(): {e}")
        return False


def get_ttacc(self, db, passed_number):
    if passed_number == 0:
        return []
    try:
        ttaccs_list = []
        doc_ref = db.collection("inuse").document('tiktok_inuse_status')
        ttaccs_dict = doc_ref.get().to_dict()
        print(f'THE NUMBER OF OVERALL AVAILABLE TTACCS: {len(ttaccs_dict)}')
        while True:
            for i in range(0, len(ttaccs_dict)):
                if ttaccs_dict[f'{str(i+1).zfill(5)}']['inuse'] == True:
                    continue
                else:
                    ttacc_address = str(i+1).zfill(5)
                    ttaccs_list.append(ttacc_address)
                if len(ttaccs_list) >= passed_number:
                    break
            break

        random.shuffle(ttaccs_list)
        print(f"fetched accounts in get_ttaccs(): {ttaccs_list}")
        update_dict = {}

        for ttacc_address in ttaccs_list:
            key = f"{ttacc_address}.inuse"
            update_dict[key] = True


        print(f"final dict to update in get_ttaccs(): {update_dict}")
        try:
            doc_ref.update(update_dict)
            # print(f"{ttacc_doc_snap_id}, updated to true successfully -- tiktokacc")
            # print(f"tt: {ttacc_doc_snap.to_dict()}")

            return ttaccs_list
        except Exception as e:
            print(f"error updating document IN GET_TTACC: {e}")
            return False

    except Exception as e:
        print(f"exception in get_ttacc(): {e}")
        return False


def free_usage_accnproxy_db(local_db, accounts, proxies):
    account_doc_inuse_truefalse = local_db.collection('inuse').document(f"tiktok_inuse_status")
    proxy_doc_inuse_truefalse = local_db.collection('inuse').document(f"proxy_inuse_status")
    try:
        update_dict = {}
        for account in accounts:
            key = f"{account}.inuse"
            update_dict[key] = False
        account_doc_inuse_truefalse.update(update_dict)
        print('success updating ttaccount status back to false after init__tt__scrape')
    except Exception as e:
        print(f"error updating tiktokacc status back to false after init_tt_acc: {e}")
    try:
        update_dict = {}
        for proxy in proxies:
            key = f"{proxy['id']}.inuse.{proxy['round']}"
            update_dict[key] = False
        proxy_doc_inuse_truefalse.update(update_dict)
        print('success updating proxy status back to false after init__tt__scrape')
    except Exception as e:
        print(f"error updating proxy status back to false after init_tt_acc: {e}")


