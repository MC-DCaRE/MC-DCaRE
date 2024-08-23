import os
from datetime import datetime

mydir = os.path.join(
        os.getcwd() +"/runfolder/datafolder",
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(mydir)

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename=mydir + '/example.log', encoding='utf-8', level=logging.DEBUG)
logger.debug('This message should go to the log file')
logger.info('So should this')
logger.warning('And this, too')
logger.error('And non-ASCII stuff, too, like Øresund and Malmö')