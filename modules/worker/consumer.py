import concurrent

import aiofiles
import aiohttp
import asyncio

from fake_useragent import UserAgent
from loguru import logger

from config import CONNECTOR_LIMIT
from modules.utils import retry


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
            logger.error(
                "aiohttp exception for %s [%s]: %s",
                url,
                getattr(e, "status", None),
                getattr(e, "message", None),
            )


@retry(aiohttp.ClientConnectionError, aiohttp.ClientError,
       aiohttp.ClientResponseError, concurrent.futures._base.TimeoutError, verbose=False)
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

    _ = await get_body(url, folder)


async def handle_tasks(task_id, work_queue, progressbar):
    while not work_queue.empty():
        current_url, folder = await work_queue.get()
        try:
            _ = await get_results(current_url, folder)
            progressbar.update()
        except Exception as e:
            logger.error('Error for Task Id {}: {},  Message {}'.format(
                str(task_id), current_url, e.__repr__()), exc_info=True)
        finally:
            work_queue.task_done()
