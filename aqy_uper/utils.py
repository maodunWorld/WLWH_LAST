import logging
import os
import coloredlogs

logger = logging.getLogger('aqy')
coloredlogs.install(level='DEBUG', logger=logger)
BASE_DIR = os.path.abspath(os.path.dirname(__name__))

