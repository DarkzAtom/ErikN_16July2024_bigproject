import sys
import random
import json
import os
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QVBoxLayout, QWidget, QComboBox, QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from datetime import datetime

import firestore_file
from firebase_admin import firestore
import globals
import app_logic
from multiprocessing import Process, Pool, current_process
import time
import threading
import shortuuid


class HelloApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tasks = []
        self.running_tasks = []
        self.history = []
        self.applied_tasks_by_daemon = []
        self.history_file = 'history.json'  # File to store history
        self.initUI()
        self.load_history()  # Load history when the app starts
        self.pool = Pool(processes=1) # the amount of max separate processes for tasks

        # daemon init section
        background_thread = threading.Thread(target=self.background_process_general_queue)
        background_thread.daemon = True
        background_thread.start()
    def initUI(self):
        self.setWindowTitle("Boost 'em Likes!")
        self.setStyleSheet(globals.dark_mode_stylesheet)

        self.tabs = QTabWidget()

        self.tab1 = QWidget()
        self.createTab1()

        self.tab2 = QWidget()
        self.createTab2()

        self.tab3 = QWidget()
        self.createTab3()

        self.tab4 = QWidget()
        self.createTab4()

        self.tabs.addTab(self.tab1, "Add task")
        self.tabs.addTab(self.tab2, "Prepared tasks")
        self.tabs.addTab(self.tab3, "Running tasks")
        self.tabs.addTab(self.tab4, "History")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.resize(1200, 730)

    def background_process_general_queue(self):
        db = firestore_file.firestore_init()
        print('Daemon BPQG has been initialised.')
        while True:
            if self.running_tasks:
                print('DAEMON VIDIT TASKI')
                # Получаем все документы, отсортированные по timestamp
                tasks_collection_ref = db.collection('tasks_queue').order_by('timestamp').stream()

                # Преобразуем StreamGenerator в список и берем первый документ
                tasks = list(tasks_collection_ref)
                aplied_tasks_by_daemon = []
                if tasks:
                    first_task_doc = tasks[-1]
                    first_task_id = first_task_doc.id
                    for task in self.running_tasks:
                        print(f"TEST DAEMONA: Processing task: {task['task_id']}")
                        task_id = str(task['task_id'])
                        if first_task_id == task_id and first_task_id not in self.applied_tasks_by_daemon:
                            print(f'VIZHU MOJ TASK PERVYM!!!: {task_id}')
                            print(f'otpravlayu task w pooooooool (daemon)')
                            acc_n_prox_num = int(task['num_likes'])
                            i_accs = 0
                            i_prox = 0
                            account = []
                            proxy = []
                            accounts = []
                            proxies = []
                            while i_accs < acc_n_prox_num or i_prox < acc_n_prox_num:
                                account = app_logic.get_ttacc(self, db, acc_n_prox_num - len(accounts))
                                proxy = app_logic.get_proxy(self, db, acc_n_prox_num - len(proxies))
                                if not account:
                                    print("All TT's accounts are busy at the moment. Waiting for the free ones..")
                                    if proxy:
                                        proxies.extend(proxy)
                                        i_prox += len(proxy)
                                    time.sleep(6)
                                    continue
                                else:
                                    accounts.extend(account)
                                    i_accs += len(account)
                                if not proxy:
                                    print("All proxies are busy at the moment. Waiting for the free ones..")
                                    time.sleep(6)
                                    continue
                                else:
                                    proxies.extend(proxy)
                                    i_prox += len(proxy)



                            print('PERED OTPRAVKOY V APPLY V POLET:')
                            print(task)
                            print(accounts)
                            print(proxies)
                            print(task['username'])
                            print(task['post_link'])
                            print(task['num_likes'])
                            self.pool.apply_async(
                                app_logic.init_tiktok_scrape,
                                args=(task, accounts, proxies, task['username'], task['post_link'], task['num_likes']),
                                callback=self.complete_task
                            )
                            task['task_queue'] = 'In process'
                            self.update_running_task_table()
                            try:
                                task_ref = db.collection('tasks_queue').document(str(task_id))
                                task_ref.delete()
                                print('UDALIL TASK Z GLOBAL QUEUE!!!!')

                            except Exception as e:
                                print("NIE UDALIL TASK Z GLOBAL QUEUEUE OSHIBKA!!!!!!")
                                print(f"e: {e}")
                                QMessageBox.critical(self, "Error", str(e))
                            self.applied_tasks_by_daemon.append(first_task_id)
                        else:
                            print('NIE MA KURWA MOJEGO TASKA')
                        time.sleep(1)
                time.sleep(5)
            time.sleep(1)

    def createTab1(self):
        self.choose_platform = QComboBox(self.tab1)
        self.choose_platform_label = QLabel('Choose the platform:', self.tab1)
        self.greet_label = QLabel("Welcome to the Boost 'em Likes!\n\nPlease, choose:\n - the platform;\n - @ of the comment's user, that needs to be boosted;\n - the link to the post where the message is;\n - the number of likes you want to send:", self.tab1)
        self.id_platform_label = QLabel("Provide the @ of the account (with @ at the beginning, example: @cocojumbo):", self.tab1)
        self.id_platform = QLineEdit(self.tab1)
        self.id_platform.setText('@vanyaux')
        self.post_link_platform_label = QLabel("Provide the link of the post where the comment at (don't forget https:// at the beginning, example: https://www.tiktok.com/@duckmovieland/video/7367368496696528133):", self.tab1)
        self.post_link_platform = QLineEdit(self.tab1)
        self.post_link_platform.setText('https://www.tiktok.com/@mike.tadziross/video/7392561042364075297')
        self.likes_number_boost_label = QLabel("Provide the number of likes to boost:", self.tab1)
        self.likes_number_boost = QSpinBox(self.tab1)
        self.likes_number_boost.setValue(1)
        self.confirm_button = QPushButton('Confirm && add to the tasks', self.tab1)

        self.confirm_button.clicked.connect(self.add_task)
        self.choose_platform.addItems(['Tik Tok', 'Instagram (in development)', 'Twitter (in development)'])
        self.choose_platform.resize(400, 30)

        font = QFont()
        font.setPointSize(10)
        self.greet_label.setFont(font)

        self.confirm_button.setStyleSheet(f"background-color: {globals.run_background_color}; color: {globals.run_text_color}")

        layout = QVBoxLayout()
        layout.addWidget(self.greet_label)
        layout.addWidget(self.choose_platform_label)
        layout.addWidget(self.choose_platform)
        layout.addWidget(self.id_platform_label)
        layout.addWidget(self.id_platform)
        layout.addWidget(self.post_link_platform_label)
        layout.addWidget(self.post_link_platform)
        layout.addWidget(self.likes_number_boost_label)
        layout.addWidget(self.likes_number_boost)
        layout.addWidget(self.confirm_button)

        self.tab1.setLayout(layout)

    def createTab2(self):
        self.greet_label = QLabel("Here are your prepared tasks. You can manage them from here, i.e. execute or delete them from the list.", self.tab2)
        self.run_all_button = QPushButton('Run All Tasks', self.tab2)
        self.delete_all_button = QPushButton('Delete All Tasks', self.tab2)

        self.run_all_button.clicked.connect(self.run_all_tasks)
        self.delete_all_button.clicked.connect(self.delete_all_tasks)

        self.table_widget = QTableWidget(0, 6, self.tab2)
        self.table_widget.setHorizontalHeaderLabels(["Platform", "ID/username", "Post's link", 'Number of likes', 'Run', 'Delete'])

        font = QFont()
        font.setPointSize(10)
        self.greet_label.setFont(font)

        self.run_all_button.setStyleSheet(f"background-color: {globals.run_background_color}; color: {globals.run_text_color}")
        self.delete_all_button.setStyleSheet(f"background-color: {globals.delete_background_color}; color: {globals.delete_text_color}")

        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_all_button)
        button_layout.addWidget(self.delete_all_button)

        layout = QVBoxLayout()
        layout.addWidget(self.greet_label)
        layout.addLayout(button_layout)
        layout.addWidget(self.table_widget)

        self.tab2.setLayout(layout)

    def createTab3(self):
        self.running_label = QLabel("These tasks are currently running:", self.tab3)

        self.running_table = QTableWidget(0, 5, self.tab3)  # 0 rows initially
        self.running_table.setHorizontalHeaderLabels(["Platform", "ID/username", "Post's link", 'Number of likes', 'Execution Status'])

        self.running_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.running_table.horizontalHeader().setStretchLastSection(True)
        self.running_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(self.running_label)
        layout.addWidget(self.running_table)

        self.tab3.setLayout(layout)

    def createTab4(self):
        self.history_label = QLabel("History of completed tasks:", self.tab4)

        self.history_table = QTableWidget(0, 6, self.tab4)  # 0 rows initially, 5 columns to include timestamp
        self.history_table.setHorizontalHeaderLabels(["Platform", "ID/username", "Post's link", 'Number of likes', 'Timestamp', 'Status'])

        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(self.history_label)
        layout.addWidget(self.history_table)

        self.tab4.setLayout(layout)

    def save_history(self):
        with open(self.history_file, 'w') as file:
            json.dump(self.history, file, default=str)

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as file:
                    content = file.read()
                    if content:  # Check if the file is not empty
                        self.history = json.loads(content)
                    else:
                        self.history = []
                self.update_history_table()
            except json.JSONDecodeError:
                self.history = []  # Reset history if JSON is invalid
                self.update_history_table()

    def add_task(self):
        platform = self.choose_platform.currentText()
        username = self.id_platform.text()
        post_link = self.post_link_platform.text()
        num_likes = self.likes_number_boost.value()

        if not username.startswith('@'):
            QMessageBox.warning(self, 'Input Error', "Username should start with '@'.")
            return
        if not post_link.startswith('https://'):
            QMessageBox.warning(self, 'Input Error', "Post link should start with 'https://'.")
            return

        task = {
            'platform': platform,
            'username': username,
            'post_link': post_link,
            'num_likes': num_likes
        }

        self.tasks.append(task)
        self.update_task_table()
        self.clear_input_fields()

    def clear_input_fields(self):
        self.choose_platform.setCurrentIndex(0)
        self.id_platform.clear()
        self.post_link_platform.clear()
        self.likes_number_boost.setValue(0)

    def update_task_table(self):
        self.table_widget.setRowCount(0)

        for task in self.tasks:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            self.table_widget.setItem(row_position, 0, QTableWidgetItem(task['platform']))
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(task['username']))
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(task['post_link']))
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(str(task['num_likes'])))

            run_button = QPushButton('Run')
            run_button.setStyleSheet(f"background-color: {globals.run_background_color}; color: {globals.run_text_color}")
            delete_button = QPushButton('Delete')
            delete_button.setStyleSheet(f"background-color: {globals.delete_background_color}; color: {globals.delete_text_color}")

            run_button.clicked.connect(lambda checked, row=row_position: self.run_task(row))
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_task(row))

            self.table_widget.setCellWidget(row_position, 4, run_button)
            self.table_widget.setCellWidget(row_position, 5, delete_button)

    def run_task(self, row):
        try:
            if globals.db is None:
                raise ValueError("Firestore database is not initialized.")
            platform = self.tasks[row]['platform']
            print('platformu s taska opoznalo')
            if platform == "Tik Tok":
                accounts_no_ref = globals.db.collection('inuse').document('tiktok_inuse_status')
                accounts_no_snap = accounts_no_ref.get()
                accounts_no = len(accounts_no_snap.to_dict())
                print(f'account number fetchnulo: {accounts_no}')
                if self.tasks[row]['num_likes'] > accounts_no:
                    QMessageBox.critical(self, "Error", f"The number of likes you've provided is bigger then the overall amount of accounts available busy and free ({accounts_no} at the moment). \nPlease, lower the number of likes for the task or ask administrator to add more accounts to the database.")
                    return False
                if isinstance(accounts_no, QMessageBox.StandardButton):
                    print('returning false, account problem')
                    return False
                proxies_no_ref = globals.db.collection('inuse').document('proxy_inuse_status')
                proxies_no_snap = proxies_no_ref.get()
                proxies_no = len(proxies_no_snap.to_dict())
                print(f'proxy number fetchnulo: {accounts_no}')
                if self.tasks[row]['num_likes'] > proxies_no*5:
                    QMessageBox.critical(self, "Error", f"The number of likes you've provided is bigger then the overall amount of proxies available busy and free ({proxies_no} at the moment). \nPlease, lower the number of likes for the task or ask administrator to add more proxies to the database.")
                    return False
                if isinstance(proxies_no, QMessageBox.StandardButton):
                    print('returning false, proxy problem')
                    return False  # Indicate an error occurred
                username = self.tasks[row]['username']
                post_link = self.tasks[row]['post_link']
                num_likes = self.tasks[row]['num_likes']
            else:
                QMessageBox.critical(self, "Error",
                                     "You can't run the program on the platforms in development. Please, delete the task with incorrect platform.")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return False  # Indicate an error occurred

        task = self.tasks.pop(row)
        task_id = id(task)  # Use the object's id as a unique identifier
        task['task_id'] = task_id  # Store the task ID in the task dictionary for logging
        task['task_queue'] = 'Waiting in queue'
        task['exec_timestamp'] = datetime.now()
        task_data_to_queue = {
            'timestamp': task['exec_timestamp']
        }
        try:
            globals.db.collection('tasks_queue').document(str(task_id)).set(task_data_to_queue)
            print('DOBAVIL V OBSHIJ QUEUE!!!!')
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.running_tasks.append(task)
        self.update_task_table()
        self.update_running_task_table()

        print('AKKAKAKAKKAprobuju applysincato (czekam na to przez daemona)')


        print(f"[{task_id}] Task submitted: {username} on {post_link}")

        return True  # Indicate success

    def complete_task(self, result):
        db = firestore_file.firestore_init()
        task, success, accounts, proxies = result
        task_id = task['task_id']
        if task in self.running_tasks:
            self.applied_tasks_by_daemon = [task_local for task_local in self.applied_tasks_by_daemon if task_local != task['task_id']]
            try:
                update_dict_ttaccs = {}
                for account in accounts:
                    key = f'{account}.inuse'
                    update_dict_ttaccs[key] = False
                print(f'Complete task: returning false from the acclist {accounts}')
                print(f'with the dictionary of accs {update_dict_ttaccs}')
                inuse_tiktok_ref = db.collection('inuse').document('tiktok_inuse_status')
                inuse_tiktok_ref.update(update_dict_ttaccs)
                print("The status False has been returned to all TT accounts after completion")
                update_dict_proxies = {}
                for proxy in proxies:
                    key = f"{proxy['id']}.inuse.{proxy['round']}"
                    update_dict_proxies[key] = False
                print(f"Complete task: returning false from the proxlist {proxies}")
                print(f"with the dictionary of proxies {update_dict_proxies}")
                inuse_proxy_ref = db.collection('inuse').document('proxy_inuse_status')
                inuse_proxy_ref.update(update_dict_proxies)
                print("The status False has been returned to all proxies after completion")
            except Exception as e:
                print(f"The error has occured while returned the False status to all accs/proxies, e: {e}")
            self.running_tasks.remove(task)
            # Add timestamp to the task
            task['timestamp'] = datetime.now().strftime('%H:%M:%S, %d/%m/%Y')
            task['status'] = 'Failed' if not success else 'Completed'
            self.history.append(task)
            self.update_running_task_table()
            self.update_history_table()
            self.save_history()  # Save history whenever it is updated
            print(f"[{task_id}] Task completed: {task['username']} on {task['post_link']} with status {task['status']}")

    def delete_task(self, row):
        del self.tasks[row]
        self.update_task_table()

    def run_all_tasks(self):
        while self.tasks:
            if not self.run_task(0):  # If run_task returns False, break the loop
                break

    def delete_all_tasks(self):
        self.tasks.clear()
        self.update_task_table()

    def update_running_task_table(self):
        self.running_table.setRowCount(0)

        for task in reversed(self.running_tasks):
            row_position = self.running_table.rowCount()
            self.running_table.insertRow(row_position)

            self.running_table.setItem(row_position, 0, QTableWidgetItem(task['platform']))
            self.running_table.setItem(row_position, 1, QTableWidgetItem(task['username']))
            self.running_table.setItem(row_position, 2, QTableWidgetItem(task['post_link']))
            self.running_table.setItem(row_position, 3, QTableWidgetItem(str(task['num_likes'])))
            self.running_table.setItem(row_position, 4, QTableWidgetItem(task['task_queue']))

    def update_history_table(self):
        self.history_table.setRowCount(0)

        for task in reversed(self.history):  # Reverse the history list to show the most recent tasks first
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)

            self.history_table.setItem(row_position, 0, QTableWidgetItem(task['platform']))
            self.history_table.setItem(row_position, 1, QTableWidgetItem(task['username']))
            self.history_table.setItem(row_position, 2, QTableWidgetItem(task['post_link']))
            self.history_table.setItem(row_position, 3, QTableWidgetItem(str(task['num_likes'])))
            self.history_table.setItem(row_position, 4, QTableWidgetItem(task['timestamp']))  # Add timestamp
            self.history_table.setItem(row_position, 5, QTableWidgetItem(task['status']))



    def remove_tasks_from_firestore_queue(self, task_id):
        db = firestore_file.firestore_init()
        try:
            task_ref = db.collection("tasks_queue").document(str(task_id))
            task_ref.delete()
            print(f"The task {task_id} has been deleted from the general queue.")
        except Exception as e:
            print(f"An error while deleting the task {task_id} from the general queue: {e}")


    def clean_up_tasks(self):
        try:
            for task in self.running_tasks:
                self.remove_tasks_from_firestore_queue(str(task['task_id']))
            print("All tasks has been removed from the general queue.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def closeEvent(self, event):
        self.pool.close()
        self.pool.join()
        self.clean_up_tasks()
        event.accept()



def main():
    app = QApplication(sys.argv)
    hello_app = HelloApp()
    hello_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
