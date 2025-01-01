import pypyodbc
from flask import Flask, render_template, redirect, request
from pathlib import Path
import smtplib
import json
import time
import os
#DBA_code == 'DBA707' and password == 'Mercury80'
class DatabaseManager:
    def __init__(self, config_file):
        with open(config_file, 'r') as json_file:
            config = json.load(json_file)
            #print(config)
        
        self.driver = (
            f"Driver={config['Driver']};"
            f"Server=tcp:{config['ServerName']},1433;"
            f"Database={config['DatabaseName']};"
            f"Uid={config['UserID']};"
            f"Pwd={config['Password']};"
            f"Encrypt={config['Encrypt']};"
            f"TrustServerCertificate={config['TrustServerCertificate']};"
            f"Connection Timeout={config['ConnectionTimeout']};"
        )
        #print(self.driver)
        self.original = []
        self.super_original = []
        self.load_data()

    def load_data(self):
        self.original = self.get_table_data('original')
        self.super_original = self.get_table_data('superoriginal')

    def get_table_data(self, table_name, all_fields=True):
        cols = "*"
        if not all_fields:
            cols = ', '.join(Columns[:-1])
        query = f"SELECT {cols} FROM {table_name}"
        with pypyodbc.connect(self.driver, autocommit=True) as cnxn:
            with cnxn.cursor() as cursor:
                cursor.execute(query)
                return [tuple(row) for row in cursor.fetchall()]


from datetime import datetime

class MailSender:
    def __init__(self, config_file):
        with open(config_file, 'r') as json_file:
            email_config = json.load(json_file)
        
        self.sender_email = email_config.get("sender_email", "")
        self.sender_password = email_config.get("sender_password", "")
        self.recipient_emails = email_config.get("recipient_emails", [])

    def send_intrusion_alert_mail(self):
        if not self.sender_email or not self.sender_password or not self.recipient_emails:
            print("Email configuration is incomplete. Cannot send email.")
            return

        subject = 'Intrusion Alert [Important]'
        message = 'Hey User, System has detected an Intrusion attempt to breach information stored on Azure Database Server. The access has been diverted. Kindly secure the servers.'
        
        for recipient_email in self.recipient_emails:
            self._send_email(recipient_email, subject, message)

    def send_operation_alert_mail(self, operation_name):
        if not self.sender_email or not self.sender_password or not self.recipient_emails:
            print("Email configuration is incomplete. Cannot send email.")
            return

        subject = f'Operation Alert by Intruder - {operation_name}'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f'Operation Name: {operation_name}\nTimestamp: {timestamp}'
        
        for recipient_email in self.recipient_emails:
            self._send_email(recipient_email, subject, message)

    def _send_email(self, recipient_email, subject, message):
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.starttls()
                smtp.login(self.sender_email, self.sender_password)
                smtp.sendmail(self.sender_email, recipient_email, f'Subject: {subject}\n\n{message}')
            print(f"Email sent to {recipient_email} with subject: {subject}")
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")



class BankCardManager:
    def __init__(self):
        self.app = Flask(__name__)
        self.genuine_DBA = True
        self.fail_count = 0
        self.make_inaccessible = False
        self.my_str = ""
        self.db_manager = DatabaseManager('config/db_config.json')
        self.email_sender = MailSender('config/email_config.json')
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/MyBankCardsManager')
        def entry_page():
            time.sleep(1)
            self.fail_count = 0
            self.genuine_DBA = True
            return render_template("1.EntryPage.html")

        @self.app.route('/MyBankCardsManager/ThisIsDBA')
        def authenticate_dba():
            time.sleep(1)
            self.fail_count = 0
            self.genuine_DBA = True
            return render_template("2.AuthenticateDBA.html")

        @self.app.route('/MyBankCardsManager/AuthenticateAgain')
        def authenticate_again():
            time.sleep(1)
            return render_template("3.AuthenticateAgain.html")

        @self.app.route('/MyBankCardsManager/DBAMenu')
        def dba_menu():
            time.sleep(1)
            return render_template("4.DBAMenu.html")

        @self.app.route('/MyBankCardsManager/ProcessDBAdata', methods=['GET'])
        def process_dbadata():
            DBA_code = request.args.get('DBACode')
            password = request.args.get('Password')
            if DBA_code == 'DBA707' and password == 'Mercury80':
                if self.fail_count in (0, 1):
                    self.genuine_DBA = True
                return redirect("http://localhost:7000/MyBankCardsManager/DBAMenu")
            else:
                self.fail_count += 1
                if self.fail_count >= 3:
                    self.genuine_DBA = False
                    self.email_sender.send_intrusion_alert_mail()
                    return redirect("http://localhost:7000/MyBankCardsManager/DBAMenu")
                return redirect("http://localhost:7000/MyBankCardsManager/AuthenticateAgain")

        @self.app.route('/MyBankCardsManager/DBAMenu/DropDB')
        def drop_db():
            time.sleep(2)
            self.db_manager.original = ['Database made inaccessible']
            self.db_manager.super_original = ['NULL, 0 records selected']
            if not self.genuine_DBA:
                self.email_sender.send_operation_alert_mail('drop_db')
            return "<h1>Dropped the database</h1>"

        @self.app.route('/MyBankCardsManager/DBAMenu/AddEntry')
        def add_entry():
            time.sleep(1)
            return render_template("6.AddEntry.html")

        @self.app.route('/MyBankCardsManager/DBAMenu/ViewDatabase')
        def view_database():
            time.sleep(1)
            self.my_str = ''
            temp = ''
            if self.genuine_DBA:
                table_name = 'original'
            else:
                self.email_sender.send_operation_alert_mail('view_database')
                table_name = 'superoriginal'
                self.make_inaccessible = True

            table_data = self.db_manager.get_table_data(table_name)
            self.my_str = f"<h1> {table_name.upper()} DATABASE </h1><br><h5>{'<br>'.join(map(str, table_data))}</h5>"
            temp = self.my_str
            self.my_str = ""
            return temp

        @self.app.route('/MyBankCardsManager/DBAMenu/DownloadDB')
        def download_db():
            time.sleep(1)
            downloads_path = str(Path.home() / "Downloads")
            file_path = f"{downloads_path}/MyBankCardsManagerDatabase.txt"
            with open(file_path, 'w') as file:
                data = self.db_manager.original if self.genuine_DBA else self.db_manager.super_original
                file.writelines('\n'.join(map(str, data)))
            if not self.genuine_DBA:
                self.email_sender.send_operation_alert_mail('download_db')
            return "<h1>Database Downloaded</h1>"

        @self.app.route('/MyBankCardsManager/DBAMenu/AddEntryData', methods=['GET'])
        def add_entry_data():
            time.sleep(1)
            card_name = request.args.get('CName')
            card_number = request.args.get('CNum')
            card_expiry = request.args.get('CExpiry')
            card_cvv = request.args.get('CCVV')
            record = (card_name, 'National Bank', card_number, card_expiry, card_cvv)

            if self.genuine_DBA:
                self.db_manager.original.append(record)
            else:
                self.email_sender.send_operation_alert_mail('add_entry_data')
                self.db_manager.super_original.append(record)
            return render_template("9.EntrySuccessful.html")

    def run(self):
        
        self.db_manager.load_data()
        print("To access application, go to:","http://127.0.0.1:7000/MyBankCardsManager\n\n\nServer Traffic and other details:\n")
        self.app.run(host="localhost", port=7000, debug=True)


def killProcessRunningAtPort(port):
    import subprocess
    port=str(port)
    command="netstat -ano | findstr :"+port
    output=subprocess.getoutput(command).split('\n')
    PIDs=[]
    for i in output:
        if "127.0.0.1:"+port in i and "LISTENING" in i:
            PIDs.append(i.split()[-1])
    for i in PIDs:
        print("Killing "+i)
        subprocess.getoutput("taskkill /PID "+i+" /F")

if __name__ == '__main__':
    killProcessRunningAtPort(port=7000)
    bank_card_manager = BankCardManager()
    bank_card_manager.run()
