from os.path import isfile
from src.backend.db_client import DataBaseClient

if __name__ == '__main__':
    if not isfile("database.db"):
        DataBaseClient.init_db()
    DataBaseClient.cursor.execute("PRAGMA foreign_keys = ON")