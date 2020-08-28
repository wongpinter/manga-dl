import os.path
from modules.worker import Worker, handle_tasks
from provider.readm import Generator
from modules.utils import logger, zipdir
from settings import MAX_THREAD, MANGA_STORAGE_PATH, CBZ_STORAGE_PATH


class Scraper:
    def __init__(self, url):
        self.url = url
        self.manga_name = ""

    def all_chapters(self):
        generator = Generator(self.url, folder_path=MANGA_STORAGE_PATH)
        logger.info("Parsing {}".format(self.url))

        chapters = generator.main()
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
