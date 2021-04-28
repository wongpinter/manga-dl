import asyncio
import concurrent.futures.thread
import pathlib
import json
import tqdm
import bs4
import re

import cloudscraper
from bs4 import BeautifulSoup
from typing import List
from loguru import logger

from .common import Common

scraper = cloudscraper.create_scraper()


class Generator(Common):
    _name = "mangakakalot.fun"
    _domain = "https://mangakakalot.fun"
    _images_cdn = "https://img.mghubcdn.com/file/imghub/"
    _api_domain = "https://api.mghubcdn.com/graphql"
    _query = """query {
                    chapter(x:mn01,slug:\"%s\", number: %f) {
                        id,
                        title,
                        mangaID,
                        number,
                        slug,
                        date,
                        pages,
                        noAd,
                        manga {
                            id
                            title,
                            slug,
                            mainSlug,
                            author,
                            isWebtoon,
                            isYaoi,
                            isPorn,
                            isSoftPorn,
                            unauthFile,
                            isLicensed
                        }
                    }
                }"""

    def __init__(self, url, folder_path):
        super().__init__(url, folder_path)

    def _book_title(self, soup: BeautifulSoup) -> None:
        title_soup = soup.find("h1", {"class": "_3xnDj"})

        if title_soup is not None:
            title = " ".join([t for t in title_soup.contents if type(t) == bs4.element.NavigableString])

            self.manga_name = title

        return None

    def _book_chapters(self):
        page = scraper.get(self.url)
        soup = BeautifulSoup(page.text, 'lxml')

        self._book_title(soup)

        result = []

        for li in soup.find_all("li", {"class": "_287KE"}):
            chapter_link = li.find("a", {"class": "_2U6DJ"})
            chapter_name = li.find("span", {"class": "_3D1SJ"})

            result.append((
                Generator._build_chapter_lists(
                    chapter_link['href'], chapter_name.text
                )
            ))

        return result

    def _book_chapter_pages(self, response) -> List:
        book = json.loads(response)

        clean_chapter_number = Generator.fix_chapter_name(book['data']['chapter']['number'])

        pages = json.loads(book['data']['chapter']['pages'])

        folder_download = pathlib.Path(self.folder_path, self.manga_name, clean_chapter_number)

        full_pages = []
        for index, page in pages.items():
            page_url = f"{self._images_cdn}{page}"
            self.page_urls.append([folder_download, page_url])

        return full_pages

    async def get_pages_url(self, chapter_urls: List) -> List:
        chapters = self._book_chapters()

        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                self.loop.run_in_executor(
                    executor,
                    self.api_fetch,
                    data
                )
                for data in chapters
            ]

            for future in tqdm.tqdm(asyncio.as_completed(futures), total=len(futures), position=0, leave=False,
                                    unit=" chapter",
                                    desc="Parsing images "
                                         "path"):
                _ = await future

            for response in await asyncio.gather(*futures):
                self._book_chapter_pages(response.text)

    def api_fetch(self, chapter):
        chapter_number, chapter_slug, chapter_url = chapter

        query = self._query % (chapter_slug, float(chapter_number))

        return scraper.post(self._api_domain, json={'query': query})

    @staticmethod
    def fix_chapter_name(numbering, width=3):
        numbering = str(numbering)

        if numbering not in ".":
            return "Chapter {}".format(numbering.zfill(width))

        bits = numbering.split('.')

        return "Chapter {}".format("%s.%s" % (bits[0].zfill(width), bits[1]))

    @staticmethod
    def _build_chapter_lists(url, chapter):
        chapter_slug = url.split("/")[-2]

        chapter_number = re.sub(r'#', '', chapter)

        return chapter_number, chapter_slug, url
