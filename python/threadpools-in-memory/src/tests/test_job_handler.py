from concurrent import futures
import pytest
import re

from mock_server import MockServerMixin
from job_handler import JobHandler
import http_utils as http
import conc_utils as conc

class TestJobHandler(MockServerMixin):

    job_handler = JobHandler('96e2154893e4610', 1, 1)
    urls = [
        'https://www.goodurl.com/image.png',
        'https://www.goodurl.com',
        ]

    def test_submit(self):
        new_job = self.job_handler.submit(self.urls)
        assert self.job_handler.jobs.get(new_job['id'], None)

    def test_process_concurrently(self):
        self.job_handler.reset()
        new_job = self.job_handler._make_job(self.urls)
        job = self.job_handler._process_concurrently(new_job)
        # After processing, jbo fields should indicate a completion.
        assert job['id'] == new_job['id']
        assert job['created'] == new_job['created']
        assert job['finished'] is not None
        assert job['status'] == 'complete'
        # _process_concurrently manipulates the job in place.
        assert job == new_job

    def test_handle_futures(self):
        self.job_handler.reset()
        new_job = self.job_handler._make_job(self.urls)
        func = self.job_handler._process_image_url
        with futures.ThreadPoolExecutor(3) as executor:
            to_do = conc.submit_to_executor(executor, func, self.urls)
        # After completion, there should be no more pending urls
        # The bad url should fail and the image url should succeed.
        job = self.job_handler._handle_futures(new_job, to_do)
        assert job['uploaded']['pending'] == []
        assert job['uploaded']['complete'] == ['https://i.imgur.com/0yco6KM.gif']
        assert job['uploaded']['fail'] == ['https://www.goodurl.com']
        assert self.job_handler.images == ['https://i.imgur.com/0yco6KM.gif']
        # _handle_futures manipulates the job in place.
        assert job == new_job

    def test_process_image_url(self):
        # A good url should result in a imgur link
        link = self.job_handler._process_image_url(self.urls[0])
        assert link == 'https://i.imgur.com/0yco6KM.gif'
        # A bad url should result in an exception
        with pytest.raises(IOError):
            link = self.job_handler._process_image_url(self.urls[1])
    
    def test_upload_to_imgur(self):
        valid_base64 = 'dGhpcyBpcyBiYXNlIDY0'
        invalid_base64 = '$%^&'
        # Given a valid base64 string, the request should be made.
        resp = self.job_handler._upload_to_imgur(valid_base64)
        assert resp.status_code == 200
        # Otherwise raise an exception before making the request to imgur.
        with pytest.raises(ValueError):
            resp = self.job_handler._upload_to_imgur(invalid_base64)

