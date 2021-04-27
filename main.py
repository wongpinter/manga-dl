#!/usr/bin/env python

import click
import tldextract

from loguru import logger

from app.fetcher import Fetcher

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>[{time:YYYY-MM-DD at HH:mm:ss}]</green> <level>{message}</level>")


@click.group()
def cli():
    pass


@click.command(options_metavar='<options>')
@click.option('--url', prompt='Manga URL', help='URL for the fetch manga')
def all_chapters(url):
    url_ext = tldextract.extract(url)

    if url_ext.domain:
        logger.info("Scraping {} Chapter Started...".format(url))

        fetch = Fetcher(provider=url_ext.domain, url=url)
        fetch.run()


cli.add_command(all_chapters, )

if __name__ == '__main__':
    cli()
