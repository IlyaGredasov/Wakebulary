import logging
from logging.handlers import RotatingFileHandler
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_file_path = os.path.join(os.path.dirname(__file__), "logs.log")
handler = RotatingFileHandler(log_file_path, encoding='utf-8')
formatter = logging.Formatter(fmt="[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
