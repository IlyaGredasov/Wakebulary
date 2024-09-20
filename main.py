from subprocess import run
from os.path import isfile

if __name__ == '__main__':
    if not isfile("database.db"):
        run(["python", "./src/backend/init_db.py"])
