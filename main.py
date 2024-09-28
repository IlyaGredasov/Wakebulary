from os.path import isfile
from src.backend.db_client import DataBaseClient
from src.backend.sample_generator import SampleGenerator

if __name__ == '__main__':
    if not isfile("database.db"):
        DataBaseClient.init_db()
    DataBaseClient.cursor.execute("PRAGMA foreign_keys = ON")
    generator = SampleGenerator("rus")
    try:
        generator.start_learning_loop()
    except KeyboardInterrupt:
        generator.session_stats.timer()
        print(generator.session_stats)
