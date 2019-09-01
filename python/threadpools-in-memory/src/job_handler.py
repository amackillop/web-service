import base64
from concurrent import futures
import datetime as dt
import logging
import requests
import uuid

from typing import List, Dict, NamedTuple, Iterable, Any
import http_utils as http
import conc_utils as conc
import reprlib
    

class JobHandler():
    """This is where the submitted jobs are handled.
    
    Posted jobs are submitted to a thread pool for future execution 

    """

    # The following attributes hold the state of the api.
    jobs: dict = {}
    images: List[str] = []

    def __init__(self, client_id: str, num_threads: int, conc_reqs: int = 1):
        """
        Args
        ----
        num_threads
            How many threads to use for the main job handling pool.
        client_id
            Id given by imgur to authorize requests to its API.
        conc_reqs
            How many threads to use for concurrent downloading/uploading tasks
            within a single job.

        Note: Free usage of the Imgur API is limited. If post requests are
              happening too quickly, Imgur will put the app in a timeout.

        """
        self._thread_pool = futures.ThreadPoolExecutor(num_threads)
        self._client_id = client_id
        # Enforce a hard limit to prevent spamming Imgur
        self._conc_reqs = min(10, conc_reqs)

    def reset(self):
        """Reset state of the API"""
        self.jobs = {}
        self.images = []

    @staticmethod
    def _make_job(urls: List[str]) -> dict:
        """Structure of posted job."""
        job = {
            'id': str(uuid.uuid4()),
            'created': dt.datetime.utcnow().isoformat(),
            'finished': None,
            'status': 'in-progress',
            'uploaded': {
                'pending': list(urls),
                'complete': [],
                'fail': [],
            },
        }
        return job
        
    def submit(self, urls: List[str]) -> dict:
        """Submits a job to the handler. Implemented as a thread pool."""
        job = self._make_job(urls)
        self.jobs[job['id']] = job
        self._thread_pool.submit(self._process_concurrently, job)
        logging.info(f'Submited job {job["id"]}')
        return dict(job)

    def _process_concurrently(self, job: dict) -> dict:
        """Download/upload data from job urls concurrently."""
        executor = futures.ThreadPoolExecutor(max_workers=self._conc_reqs)
        urls = job['uploaded']['pending']
        to_do = conc.submit_to_executor(executor, self._process_image_url, urls)
        job = self._handle_futures(job, to_do)
        job['finished'] = dt.datetime.utcnow().isoformat()
        job['status'] = 'complete'
        executor.shutdown(wait=True)
        return job

    def _handle_futures(self, job: dict, to_do: List[futures.Future]) -> dict:
        """Handle futures as they complete. Update state upon each completion."""
        future_iter = futures.as_completed(to_do)
        pending = job['uploaded']['pending']
        fails = job['uploaded']['fail']
        complete = job['uploaded']['complete']

        for future in future_iter:
            fut_result = conc.get_future_result(future, to_do)
            url = pending.pop(pending.index(fut_result.args))
            if isinstance(fut_result, conc.Fail):
                fails.append(url)
                logging.info(f'{job["id"]}: FAIL! {url} -> {fut_result.reason}')
            else:
                complete.append(fut_result.result)
                self.images.append(fut_result.result)
                logging.info(f'{job["id"]}: SUCCESS! {url} -> {fut_result.result}')
        return job

    def _process_image_url(self, url : str) -> str:
        """From target URL, download image then upload it to Imgur."""
        dl_resp = http.download_image(url)
        logging.debug(f'Download response: {url} -> {reprlib.repr(dl_resp.content)}')
        image = base64.b64encode(dl_resp.content).decode('ascii')
        imgur_resp = self._upload_to_imgur(image)
        logging.debug(f'Upload response from Imgur: {url} -> {imgur_resp.json()}')
        link = imgur_resp.json()['data']['link']
        return link

    def _upload_to_imgur(self, image_as_b64: str) -> requests.Response:
        """Given a base 64 string, upload it as an image to Imgur."""
        url = 'https://api.imgur.com/3/image'
        try:
            base64.b64decode(image_as_b64, validate=True)
        except base64.binascii.Error:
            msg = 'image_as_b64 needs to be a valid base-64 string.'
            raise ValueError(msg)
        data = {'image': image_as_b64}
        headers = {'Authorization': f'Client-ID {self._client_id}'}
        resp = http.make_request('POST', url, headers=headers, data=data)
        return resp
