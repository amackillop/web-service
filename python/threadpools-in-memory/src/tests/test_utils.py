from concurrent import futures
import pytest
import requests

import http_utils as http
import conc_utils as conc
from mock_server import MockServerMixin

class TestHttp(MockServerMixin):

    def test_make_request(self):
            # Successful request should return.
            resp = http.make_request('get', 'https://www.goodurl.com')
            assert resp.status_code == 200
            # Bas requests should raise an HTTPError
            with pytest.raises(requests.exceptions.HTTPError):
                http.make_request('get', 'https://www.badrequest.com')
        
    def test_download_image(self):
        # Going to an image should be successful
        resp = http.download_image('https://www.goodurl.com/image.png')
        assert resp.status_code == 200
        # Going to a webpage should fail with an IOError
        with pytest.raises(IOError):
            http.download_image('https://www.goodurl.com')

class TestConc():
    executor = futures.ThreadPoolExecutor(3)
    @staticmethod
    def func(a, b): a + b
    args_tuples = [(1,2), (3,4), (5,)]

    def test_submit_to_executor(self):
        to_do = conc.submit_to_executor(self.executor, self.func, self.args_tuples)
        for future, args in to_do.items():
            assert isinstance(future, futures.Future)
            assert args in self.args_tuples
        assert len(to_do) == len(self.args_tuples)
    
    def test_get_future_result(self):
        to_do = conc.submit_to_executor(self.executor, self.func, self.args_tuples)
        for future, args in to_do.items():
            fut_result = conc.get_future_result(future, to_do)
            if args == (5,):
                assert isinstance(fut_result, conc.Fail)
            else:
                assert isinstance(fut_result, conc.Success)
                assert fut_result.result == self.func(*args)