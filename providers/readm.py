import re
import requests
import pathlib

from bs4 import BeautifulSoup
from natsort import natsorted
from loguru import logger

from .common import Common


class Generator(Common):
    _name = "readm.org"
    _domain = "https://www.readm.org"

    def __init__(self, url, folder_path):
        super().__init__(url, folder_path)

    def _book_title(self, soup: BeautifulSoup) -> None:
        title = soup.find('h1', {"class": "page-title"})

        if title is not None:
            self.manga_name = title.text

    def _book_chapters(self):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'lxml')

        section = soup.find('section', {'class': 'episodes-box'})

        self._book_title(soup)

        chapter_urls = []
        for link in section.find_all('td', {'class', 'table-episodes-title'}):
            chapter_urls.append(f"{self._domain}{link.find('a')['href']}")

        return natsorted(chapter_urls)

    @staticmethod
    def parsing_chapter_name(soup: BeautifulSoup) -> str:
        chapter = soup.find('span', {'class': 'light-title'})

        if chapter is None:
            return None

        chapter_number = re.search(r'Chapter (.+)', chapter.text)
        chapter_number_name = Generator.fix_chapter_name(chapter_number.group(1))

        return chapter_number_name

    @staticmethod
    def fix_chapter_name(numbering, width=3):
        if numbering not in ".":
            return "Chapter {}".format(numbering.zfill(width))

        bits = numbering.split('.')
        return "Chapter {}".format("%s.%s" % (bits[0].zfill(width), bits[1]))

    async def _book_chapter_pages(self, response):
        result_chapter = []

        soup = BeautifulSoup(response, 'lxml')

        if soup is None:
            return result_chapter

        links = soup.find("div", {'class': "ch-images ch-image-container"})

        chapter = Generator.parsing_chapter_name(soup)

        if chapter is None:
            return result_chapter

        folder_download = pathlib.Path(self.folder_path, self.manga_name, chapter)

        for link in links.find_all('img', {'class': 'img-responsive scroll-down'}):
            image_url = f"{self._domain}{link['src']}"

            self.page_urls.append([folder_download, image_url])

        return result_chapter
