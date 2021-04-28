import tqdm
import asyncio
import aiohttp

from bs4 import BeautifulSoup
from typing import List
from loguru import logger

from config import MAX_THREAD
from modules.utils import retry


class Common(object):
    page_urls = []
    manga_name = None
    limit = MAX_THREAD
    loop = asyncio.get_event_loop()

    def __init__(self, url, folder_path):
        self.url = url
        self.folder_path = folder_path

    def get_manga_name(self):
        return self.manga_name

    def _book_title(self, soup: BeautifulSoup) -> None:
        pass

    def _book_chapters(self):
        pass

    async def _book_chapter_pages(self, response) -> List:
        pass

    async def fetch(self, url, session):
        async with session.get(url) as response:
            response = await response.text()
            return await self._book_chapter_pages(response)

    async def fetch_with_limit(self, limit, url, session):
        async with limit:
            await self.fetch(url, session)

    async def do_fetch(self, session, list_urls):
        tasks = []
        limit = asyncio.Semaphore(self.limit)

        for i in list_urls:
            task = asyncio.ensure_future(self.fetch_with_limit(limit, i, session))
            tasks.append(task)

        for future in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), position=0, leave=False, unit=" chapter",
                                desc="Parsing images "
                                     "path"):
            _ = await future

    @retry(aiohttp.ClientConnectionError, aiohttp.ClientError,
           aiohttp.ClientResponseError, verbose=False)
    async def get_pages_url(self, chapter_urls: List) -> List:
        connector = aiohttp.TCPConnector(limit=None)

        async with aiohttp.ClientSession(connector=connector) as session:
            await self.do_fetch(session, chapter_urls)

    def run(self):
        chapter_urls = self._book_chapters()

        self.loop.run_until_complete(self.get_pages_url(chapter_urls))

        logger.info(f"Manga name: {self.manga_name}. Total Chapter {len(chapter_urls)}, "
                    f"Total images {len(self.page_urls)}")

        return self.page_urls
