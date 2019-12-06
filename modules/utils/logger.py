import logging

format_message = logging.Formatter('[%(asctime)s]:%(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(format_message)

logger = logging.getLogger(__name__)
logger.addHandler(handler)