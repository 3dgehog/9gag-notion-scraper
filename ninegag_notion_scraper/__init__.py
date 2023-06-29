import logging
from dotenv import load_dotenv

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
error_file_handler = logging.FileHandler('error.log')
error_file_handler.setLevel(logging.WARN)

console_handler.setFormatter(
    logging.Formatter('%(levelname)s - %(name)s - %(message)s')
)
error_file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
)

logger.addHandler(console_handler)
logger.addHandler(error_file_handler)

load_dotenv()
