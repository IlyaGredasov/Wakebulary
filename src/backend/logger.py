import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("logs.log", maxBytes=1024, backupCount=100)
formatter = logging.Formatter(fmt="[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
