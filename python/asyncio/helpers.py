
import imghdr
import requests
import base64
from io import BytesIO
import reprlib
from urllib.parse import urlparse
from collections import deque
import itertools
import aiohttp
import contextlib
import collections

from my_types import *

# HTTP stuff
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
    except:
        return False
    return all([result.scheme in ['http', 'https'], result.netloc, result.path])

@contextlib.asynccontextmanager
async def make_request(method: str, url: str, **kwargs) -> AsyncIterator:
    try:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with getattr(session, method)(url) as resp:
                yield resp
    finally:
        pass


async def download_image(url: str) -> str:
    """Download and verify image from given URL."""
    async with make_request('get', url) as resp:
        content = await resp.read()

    # Weak check that the page content is actually an image. 
    if imghdr.what(BytesIO(content)) is None:
        msg = f'Not a valid image at {url}.'
        raise IOError(msg)
    return base64.b64encode(content).decode('ascii')


# Functional Programming FTW
# def take(n, iterable):
#     "Return first n items of the iterable as a list"
#     return list(islice(iterable, n))

def tail(iterable: Iterable) -> Iterable:
    "Return an iterator over the last n items"
    deq = collections.deque(iterable)
    deq.popleft()
    return deq

def partition(predicate: Callable[[T], bool] , iterable: Iterable[T]) -> Tuple[Iterator[T], Iterator[T]]:
    'Use a predicate to partition entries into false entries and true entries'
    t1, t2 = itertools.tee(iterable)
    return filter(predicate, t1), itertools.filterfalse(predicate, t2)
