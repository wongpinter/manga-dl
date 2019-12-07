import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.curdir)
load_dotenv(dotenv_path="{}/.env".format(ROOT_DIR))

DOMAIN_URL = os.getenv("DOMAIN_URL")
MAX_THREAD = int(os.getenv("MAX_THREAD"))
MANGA_STORAGE_PATH = os.getenv("MANGA_STORAGE_PATH")
CBZ_STORAGE_PATH = os.getenv("CBZ_STORAGE_PATH")
