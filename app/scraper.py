from modules.worker import Worker, handle_tasks
from provider.async_generator import Generator
from modules.utils import logger
from settings import MAX_THREAD, MANGA_STORAGE_PATH


class Scraper:
    def __init__(self, url):
        self.url = url

    def all_chapters(self):
        generator = Generator(self.url, folder_path=MANGA_STORAGE_PATH)
        logger.info("Parsing {}".format(self.url))

        return generator.main()

    def run(self):
        worker = Worker(self.all_chapters(), handle_tasks, MAX_THREAD)
        worker.run()
