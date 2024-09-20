from logger import logger
from db_client import DataBaseClient

DataBaseClient.cursor.execute(
    """
    DROP TABLE IF EXISTS rus
    """
)
logger.info("rus table was dropped")
DataBaseClient.cursor.execute(
    """
    DROP TABLE IF EXISTS eng
    """
)
logger.info("eng table was dropped")
DataBaseClient.cursor.execute(
    """
    DROP TABLE IF EXISTS eng_rus
    """
)
logger.info("eng_rus table was dropped")
DataBaseClient.cursor.execute(
    """
    CREATE TABLE rus(
        id INTEGER PRIMARY KEY,
        word VARCHAR(255) UNIQUE NOT NULL,
        correct INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 0
    )
    """
)
logger.info("rus table was created")
DataBaseClient.cursor.execute(
    """
    CREATE TABLE eng(
        id INTEGER PRIMARY KEY,
        word VARCHAR(255) UNIQUE NOT NULL,
        correct INTEGER DEFAULT 0,
        attempts INTEGER DEFAULT 0
    )
    """
)
logger.info("eng table was created")
DataBaseClient.cursor.execute(
    """
    CREATE TABLE eng_rus(
        id INTEGER PRIMARY KEY,
        eng_id INTEGER NOT NULL,
        rus_id INTEGER NOT NULL,
        FOREIGN KEY(eng_id) REFERENCES eng(id) ON DELETE CASCADE,
        FOREIGN KEY(rus_id) REFERENCES rus(id) ON DELETE CASCADE,
        UNIQUE (eng_id, rus_id)
    )
    """
)
logger.info("eng_rus table was created")
