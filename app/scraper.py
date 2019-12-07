from modules.worker import Worker, handle_tasks
from provider.async_generator import Generator
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

    def run(self):
        worker = Worker(self.all_chapters(), handle_tasks, MAX_THREAD)
        worker.run()

        manga = "{}/{}".format(MANGA_STORAGE_PATH, self.manga_name)
        zipdir(basedir=manga, archive_name="{}/{}.cbz".format(CBZ_STORAGE_PATH, self.manga_name))
