import asyncio
import tqdm

from loguru import logger


class Producer:
    def __init__(self, urls, handle_tasks, max_threads):
        self.loop = asyncio.new_event_loop()
        self.urls = urls
        self.handle_tasks = handle_tasks
        self.max_threads = max_threads

    def run(self):
        queue = asyncio.Queue()

        [queue.put_nowait([url, folder_name]) for folder_name, url in self.urls]

        logger.info("Proccessing {} images".format(queue.qsize()))

        progressbar = tqdm.tqdm(
            desc="Scraping Proggress", total=queue.qsize(), position=0, leave=False, unit=' images'
        )

        asyncio.set_event_loop(self.loop)
        tasks = [self.handle_tasks(task_id, queue, progressbar) for task_id in range(self.max_threads)]

        try:
            self.loop.run_until_complete(asyncio.wait(tasks))
        finally:
            self.loop.close()
            progressbar.clear()
            logger.info("Scraping Done.")
