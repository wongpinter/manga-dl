import requests
import pathlib
import json
import tqdm
import aiohttp
from bs4 import BeautifulSoup
from natsort import natsorted
from modules.utils import logger
import asyncio


def chapter_name(numbering, width=3):
    if not "." in numbering:
        return "Chapter {}".format(numbering.zfill(width))

    bits = numbering.split('.')
    return "Chapter {}".format("%s.%s" % (bits[0].zfill(width), bits[1]))


def parsing_chapter_name(chapter_url):
    chapters = chapter_url.rsplit('/', 2)

    manga_name = chapters[1]
    chapter_number = chapters[2].rsplit('-', 1)[1]

    return manga_name, chapter_number


class Generator:
    def __init__(self, main_url, folder_path='Mangas'):
        self.limit = 50
        self.all_urls = []
        self.url = main_url
        self.manga_name = ""
        self.folder_path = folder_path
        self.loop = asyncio.get_event_loop()

    def parse_chapters(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')

        section = soup.find('div', {'class': 'tab-content'})

        chapter_urls = []
        for link in section.find_all('li', {"class": "list-group-item"}):
            chapter_urls.append(link.find("a")['href'])

        return natsorted(chapter_urls)

    async def parse_graph_results(self, response):
        result_chapter = []
        chapters = json.loads(response['data']['chapter']['pages'])
        chapter_number = str(response['data']['chapter']['number'])
        manga_name = response['data']['chapter']['manga']['title']

        self.manga_name = manga_name

        folder_download = pathlib.Path(self.folder_path, manga_name, chapter_name(chapter_number))

        for chapter in chapters:
            image_url = "https://cdn.mangahub.io/file/imghub/{}".format(chapters[chapter])
            self.all_urls.append([folder_download, image_url])

        return result_chapter

    async def fetch(self, url, session):
        manga_name, chapter_number = parsing_chapter_name(url)

        query = "{chapter(x:mn01, slug:\"" + manga_name + "\", number:" + str(
            chapter_number) + "){id,title,mangaID,number,slug,date,pages,noAd,manga{id,title,slug,mainSlug,author," \
                              "isWebtoon,isYaoi,isPorn,isSoftPorn,unauthFile,isLicensed}}}"

        url = 'https://api2.mangahub.io/graphql'
        async with session.post(url, json={'query': query}) as response:
            json_response = await response.json()
            return await self.parse_graph_results(json_response)

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

        logger.info("Manga name: {}. Total Chapter {}, Total images {}".format(self.manga_name, len(chapter_urls), len(self.all_urls)))

        return self.all_urls
