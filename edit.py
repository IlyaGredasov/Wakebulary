import code
from src.backend.db_client import DataBaseClient
db = DataBaseClient("database.db")
code.interact(local=locals())
