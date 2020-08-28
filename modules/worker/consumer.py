import concurrent

import aiofiles
import aiohttp
import asyncio

from modules.utils import logger, retry
from fake_useragent import UserAgent

ua = UserAgent()


def user_agent():
    return {
        "USER-AGENT": ua.chrome
    }


async def get_body(url, folder):
    header = user_agent()
    connector = aiohttp.TCPConnector(limit=30, ttl_dns_cache=33600)

    async with aiohttp.ClientSession(connector=connector, headers=header) as session:
        try:
            return await fetch(session, url, folder)
        except (
                aiohttp.ClientConnectionError
        ) as e:
            logger.debug(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )


@retry(aiohttp.ClientConnectionError, aiohttp.ClientError, asyncio.exceptions.TimeoutError, aiohttp.ClientResponseError, concurrent.futures._base.TimeoutError, verbose=False)
async def fetch(session, url, folder_name):
    image_filename = "_empty.jpg"
    if url.find('/'):
        image_filename = url.rsplit('/', 1)[1]

    filepath = folder_name.joinpath(image_filename)

    async with session.get(url, timeout=60) as response:
        f = await aiofiles.open(filepath, mode='wb')
        await f.write(await response.read())
        await f.close()


async def get_results(url, folder):
    folder.mkdir(parents=True, exist_ok=True)

    html = await get_body(url, folder)


async def handle_tasks(task_id, work_queue, progressbar, options):
    while not work_queue.empty():
        current_url, folder = await work_queue.get()
        try:
            task_status = await get_results(current_url, folder)
            progressbar.update()
        except Exception as e:
            logger.exception('Error for {}'.format(
                current_url), exc_info=True)
        finally:
            work_queue.task_done()
