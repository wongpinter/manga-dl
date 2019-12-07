#!/usr/bin/env python

import click

from modules.utils import logger


@click.group()
def cli():
    pass


@click.command(options_metavar='<options>')
@click.option('--url', prompt='Manga URL', help='Mangafun URL for the manga')
def all_chapters(url):
    from app.scraper import Scraper

    scraper = Scraper(url)

    logger.info("Scraping {} Chapter Started...".format(url))
    scraper.run()


cli.add_command(all_chapters, )

if __name__ == '__main__':
    cli()
