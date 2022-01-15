import logging

logger = logging.getLogger('app')
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
error_file_handler = logging.FileHandler('error.log')
error_file_handler.setLevel(logging.WARN)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)
error_file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(error_file_handler)
