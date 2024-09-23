import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs.log", maxBytes=1024, backupCount=100, encoding='utf-8')

formatter = logging.Formatter(fmt="[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logger.addHandler(handler)
