README
 

Introduction
MyBankCardManager is an application designed to manage and monitor bank cards in a secure environment. The system is built to detect unauthorized access attempts, notify administrators, and divert attackers to a honeypot, ensuring that genuine data remains uncompromised.



Features
User Authentication: A multi-stage user authentication system to ensure that only authorized users access the system.
Database Management: Seamless interaction with a secure database system to manage bank card details.
Email Alerts: Automated alerts for potential intrusion attempts.
Honeypot System: Redirects unauthorized users to a decoy database, safeguarding genuine data.


System Requirements
Python 3.x
Flask
pypyodbc: For database connectivity
SMTP server access for email notifications


Setup & Installation
Clone the repository or download the source code.
Navigate to the project directory.
Install required packages:  pip install Flask pypyodbc
Set up your database and email configurations in config/db_config.json and config/email_config.json, respectively.
Run the application: python main.py
Access the application by navigating to: http://127.0.0.1:7000/MyBankCardsManager


Application Structure
The project is structured to ensure modularity and ease of maintenance:

DatabaseManager: A class responsible for interacting with the database system, fetching records, and managing data.
MailSender: A class responsible for sending email alerts.
BankCardManager: The primary application class, responsible for setting up routes, handling requests, and integrating with the DatabaseManager and MailSender.


 

Security
User Authentication: The application employs a multi-level user authentication system, ensuring that unauthorized access is minimized.
Honeypot Strategy: Unauthorized access attempts are diverted to a decoy database, ensuring that genuine data remains uncompromised.
Email Alerts: Administrators are notified of potential intrusion attempts, ensuring prompt action.
Sensitive Data Handling: Sensitive information, such as passwords and card details, are handled securely, ensuring data privacy.