import os
from datetime import datetime
import logging

mydir = os.path.join(
        os.getcwd() +"/runfolder/datafolder",
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(mydir)

logger = logging.getLogger(__name__)
logname = mydir + '/example.log'
logging.basicConfig(filename= logname , encoding='utf-8', level=logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Create a file handler to write logs to a file
file_handler = logging.FileHandler(logname)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create a stream handler to print logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # You can set the desired log level for console output
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Now you can log messages with different levels
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')