from subprocess import run
from os.path import isfile
from src.backend.db_client import DataBaseClient

if __name__ == '__main__':
    if not isfile("database.db"):
        run(["python", "./src/backend/init_db.py"])
    DataBaseClient.cursor.execute("PRAGMA foreign_keys = ON")
    DataBaseClient.insert_word("Rus",["Рус"])
    DataBaseClient.delete_word("Rus")