import pypyodbc
import json
import time

def load_db_config(filename):
    with open(filename, 'r') as config_file:
        return json.load(config_file)

def establish_db_connection(config):
    try:
        conn = pypyodbc.connect(
            f"Driver={config['Driver']};"
            f"Server=tcp:{config['ServerName']},1433;"
            f"Database={config['DatabaseName']};"
            f"Uid={config['UserID']};"
            f"Pwd={config['Password']};"
            f"Encrypt={config['Encrypt']};"
            f"TrustServerCertificate={config['TrustServerCertificate']};"
            f"Connection Timeout={config['ConnectionTimeout']};"
        )
        return conn
    except Exception as e:
        print("Error connecting to the database:", str(e))
        return None

def test_connection(connection):
    if connection:
        print("MyBankCardsManager Database connection successful.")
    else:
        print("MyBankCardsManager Database connection failed.")

def main():
    config = load_db_config('config/db_config.json')
    start = time.time()
    connection = establish_db_connection(config)
    print(f"Server Name: {config['ServerName']}")
    print(f"Database Name: {config['DatabaseName']}")
    print(f"User Name: {config['UserID']}")
    print()
    # Test the database connection
    test_connection(connection)
    print(f"Test connection established in {int(time.time() - start)} seconds")


if __name__ == "__main__":
    main()
