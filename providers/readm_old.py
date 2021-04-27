import requests
import pathlib
import json
import tqdm
import re
import aiohttp
from bs4 import BeautifulSoup
from natsort import natsorted
from modules.utils import logger
import asyncio


def chapter_name(numbering, width=3):
    if numbering not in ".":
        return "Chapter {}".format(numbering.zfill(width))

    bits = numbering.split('.')
    return "Chapter {}".format("%s.%s" % (bits[0].zfill(width), bits[1]))


def parsing_chapter_name(soup):
    chapter = soup.find('span', {'class': 'light-title'})

    if chapter is None:
        return None

    chapter_number = re.search(r'Chapter (.+)', chapter.text)
    chapter_number_name = chapter_name(chapter_number.group(1))

    return chapter_number_name


class Generator:
    def __init__(self, main_url, folder_path='Mangas'):
        self.limit = 50
        self.all_urls = []
        self.url = main_url
        self.manga_name = ""
        self.folder_path = folder_path
        self.loop = asyncio.get_event_loop()

    def parse_manga_title(self, soup):
        title = soup.find('h1', {"class": "page-title"})

        if title is not None:
            self.manga_name = title.text

    def parse_chapters(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')

        section = soup.find('section', {'class': 'episodes-box'})

        self.parse_manga_title(soup)

        chapter_urls = []
        for link in section.find_all('td', {'class', 'table-episodes-title'}):
            chapter_urls.append("https://www.readm.org{}".format(link.find("a")['href']))

        return natsorted(chapter_urls)

    async def parse_manga_chapters(self, response):
        result_chapter = []

        soup = BeautifulSoup(response, 'lxml')

        if soup is None:
            return result_chapter

        links = soup.find("div", {'class': "ch-images ch-image-container"})

        chapter = parsing_chapter_name(soup)

        if chapter is None:
            return result_chapter

        folder_download = pathlib.Path(self.folder_path, self.manga_name, chapter)

        for link in links.find_all('img', {'class': 'img-responsive scroll-down'}):
            image_url = "https://www.readm.org{}".format(link['src'])
            self.all_urls.append([folder_download, image_url])

        return result_chapter

    async def fetch(self, url, session):
        async with session.get(url) as response:
            response = await response.text()
            return await self.parse_manga_chapters(response)

    async def limiting_fetch(self, semp, url, session):
        async with semp:
            await self.fetch(url, session)

    async def run(self, session, list_urls):
        tasks = []
        # create instance of Semaphore
        sem = asyncio.Semaphore(self.limit)
        for i in list_urls:
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(self.limiting_fetch(sem, i, session))
            tasks.append(task)

        for future in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks), position=0, leave=False, unit=" chapter",
                                desc="Parsing images "
                                     "path"):
            result = await future

    async def parse_all_urls(self, chapter_urls):
        connector = aiohttp.TCPConnector(limit=None)
        async with aiohttp.ClientSession(connector=connector) as session:
            await self.run(session, chapter_urls)

    def get_manga_name(self):
        return self.manga_name

    def main(self):
        chapter_urls = self.parse_chapters()

        self.loop.run_until_complete(self.parse_all_urls(chapter_urls))

        logger.info("Manga name: {}. Total Chapter {}, Total images {}".format(self.manga_name, len(chapter_urls),
                                                                               len(self.all_urls)))

        return self.all_urls
