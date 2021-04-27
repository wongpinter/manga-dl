import os.path

from loguru import logger

from providers import provider as provider_module
from modules.worker import Worker, handle_tasks
from modules.utils import zipdir
from config import MAX_THREAD, MANGA_STORAGE_PATH, CBZ_STORAGE_PATH


class Fetcher:
    manga_name = None

    def __init__(self, provider, url):
        _module = Fetcher._init_provider_module(provider)

        self.generator = _module.Generator
        self.url = url

    @staticmethod
    def _init_provider_module(provider):
        provider_module.provider_name = provider
        _module = __import__(f'providers.{provider}', globals(), locals(), ['Generator'])

        return _module

    def all_chapters(self):
        generator = self.generator(self.url, folder_path=MANGA_STORAGE_PATH)
        logger.info("Parsing {}".format(self.url))

        chapters = generator.run()
        self.manga_name = generator.get_manga_name()

        return chapters

    def create_cbz(self):
        manga = "{}/{}".format(MANGA_STORAGE_PATH, self.manga_name)

        if os.path.isdir(CBZ_STORAGE_PATH) is False:
            os.mkdir(CBZ_STORAGE_PATH)

        zipdir(basedir=manga, archive_name="{}/{}.cbz".format(CBZ_STORAGE_PATH, self.manga_name))

        logger.info("Creating CBZ file success.")

    def run(self):
        worker = Worker(self.all_chapters(), handle_tasks, MAX_THREAD)
        worker.run()

        self.create_cbz()
