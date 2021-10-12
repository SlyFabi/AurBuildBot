import logging
import requests
from datetime import datetime

from Bot.Config import LOG_DIR

# Setup existing loggers
logging.root.setLevel(logging.NOTSET)
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('waitress').setLevel(logging.ERROR)

# Setup logger
logFormatter = logging.Formatter("[%(asctime)s] %(message)s")
rootLogger = logging.getLogger()

logFile = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
LOG_PATH = "{0}/{1}.log".format(LOG_DIR, logFile)

fileHandler = logging.FileHandler(LOG_PATH)
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
if __debug__:
    consoleHandler.setLevel(logging.DEBUG)
rootLogger.addHandler(consoleHandler)


def getLogger():
    return rootLogger
