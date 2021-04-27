import os
from loguru import logger
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv('.env'))

ROOT_DIR = os.path.abspath(os.curdir)
MAX_THREAD = int(os.getenv("MAX_THREAD"))
MANGA_STORAGE_PATH = os.getenv("MANGA_STORAGE_PATH")
CBZ_STORAGE_PATH = os.getenv("CBZ_STORAGE_PATH")
CONNECTOR_LIMIT = os.getenv("CONNECTOR_LIMIT")
