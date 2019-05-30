import imghdr
import requests
import base64
from io import BytesIO
import reprlib

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
