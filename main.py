#!/usr/bin/env python

import click

from modules.utils import logger


@click.group()
def cli():
    pass


@click.command()
def all_chapters():
    from app.scraper import Scraper

    url = click.prompt("Manga URL")

    scraper = Scraper(url)

    logger.info("Scraping {} Chapter Started...".format(url))
    scraper.run()


cli.add_command(all_chapters)

if __name__ == '__main__':
    cli()
