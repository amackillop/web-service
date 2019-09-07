
import imghdr
import requests
import base64
from io import BytesIO
import reprlib
from urllib.parse import urlparse
from collections import deque
import itertools
import aiohttp

from my_types import *

# HTTP stuff
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
    except:
        return False
    return all([result.scheme in ['http', 'https'], result.netloc, result.path])

async def make_request(method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with getattr(session, method)() as resp:
            if resp.status < 200 or resp.status >= 300:
                resp.raise_for_status()
            await resp

async def download_image(url: str) -> str:
    """Download and verify image from given URL."""
    resp = make_request('get', url)
    # Weak check that the page content is actually an image. 
    if imghdr.what(BytesIO(resp.content)) is None:
        msg = f'Not a valid image at {url}.'
        raise IOError(msg)
    await base64.b64encode(resp.text()).decode('ascii')


# Functional Programming FTW
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def tail(iterable):
    "Return an iterator over the last n items"
    return iterable[1:]

def partition(predicate: Callable[[T], bool] , iterable: Iterable[T]) -> Tuple[Iterator[T], Iterator[T]]:
    'Use a predicate to partition entries into false entries and true entries'
    t1, t2 = itertools.tee(iterable)
    return filter(predicate, t1), itertools.filterfalse(predicate, t2)
