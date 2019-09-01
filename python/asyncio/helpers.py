
import imghdr
import requests
import base64
from io import BytesIO
import reprlib
from urllib.parse import urlparse
from collections import deque
import itertools

from my_types import *

# HTTP stuff
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
    except:
        return False
    return all([result.scheme in ['http', 'https'], result.netloc, result.path])

def make_request(method: str, url: str, **kwargs) -> requests.Response:
    """Make a request. Raises an exception if unsuccessful."""
    resp = requests.request(method, url, **kwargs)
    if resp.status_code < 200 or resp.status_code >= 300:
        resp.raise_for_status()
    return resp

def download_image(url: str) -> requests.Response:
    """Download and verify image from given URL."""
    resp = make_request('GET', url)
    # Weak check that the page content is actually an image. 
    if imghdr.what(BytesIO(resp.content)) is None:
        msg = f'Not a valid image at {url}.'
        raise IOError(msg)
    return resp


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
