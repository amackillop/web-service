import base64
from unittest import mock
import requests


class MockResponse:
    def __init__(self, content=None, json=None, status_code=200):
        self.json_data = json
        self.content = content
        self.status_code = status_code

    def json(self):
        return self.json_data

    def raise_for_status(self):
        raise requests.exceptions.HTTPError('Mock HTTP Error')

class MockServerMixin:

    @classmethod
    def setup_class(cls):
        cls.mock_request_patcher = mock.patch(
            'requests.request', 
            side_effect=mock_server
            )
        cls.mock_request = cls.mock_request_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_request_patcher.stop()

def mock_server(*args, **kwargs):
    method = args[0]
    url = args[1]

    img_bytes = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\'x00\x00\x00\x05\x00\x00\x00\x05'
        b'\x02\x03\x00\x00\x00\xf0\x01\xcev\x00\x00\x00\x0cPLTE\xcc\xcc\xcc\x00'
        b'\x00\x00\x99\x99\x99\x7f\x7f\x7f\xb8\xf0x\xa2\x00\x00\x00\tpHYs\x00\x00'
        b'\x0e\xc4\x00\x00\x0e\xc4\x01\x95+\x0e\x1b\x00\x00\x00\x11IDAT\x08\x99c`'
        b'\x00\x83&\x06\x06\x1b\x10\x02\x00\x05\xc3\x00\xfb\xadp\xfe\x04\x00\x00'
        b'\x00\x00IEND\xaeB`\x82'
        )
    mock_imgur_data = {
    "data": {
            "link":"https://i.imgur.com/0yco6KM.gif"
            },
        }

    if url == 'https://www.goodurl.com/image.png' and method.upper() == 'GET':
        return MockResponse(content=img_bytes)
    elif url == 'https://www.goodurl.com' and method.upper() == 'GET':
        return MockResponse(content=b'<html>random web content</html>')
    elif url == 'badurl.com' and method.upper() == 'GET':
        raise requests.exceptions.MissingSchema(('Mock Invalid URL'))
    elif url == 'https://www.badrequest.com' and method.upper() == 'GET':
        raise requests.exceptions.HTTPError('Mock HTTP Error')
    elif url == 'https://api.imgur.com/3/image' and method.upper() == 'POST':
        try:
            base64.b64decode(kwargs['data']['image'])
        except base64.binascii.Error:
            msg = 'MOCK Server: Bad Imgur request. Need image data as base64.'
            raise requests.exceptions.HTTPError(msg)
        return MockResponse(json=mock_imgur_data)
    urls = [
        'https://www.goodurl.com/image.png',
        'https://www.goodurl.com',
        'badurl.com',
        'https://www.badrequest.com',
        'https://api.imgur.com/3/image'
        ]
    msg = f'Invalid url {url} for request mocker.\nAvailable mock urls: {urls}'
    raise NameError(msg)