import asyncio
from aiohttp import web
import itertools
import requests
from functools import wraps

from dataclasses import replace, astuple
from my_types import *
import base64
import helpers as hf
import os

routes = web.RouteTableDef()

def background(func: Func) -> Func:
    @wraps(func)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, func, *args, **kwargs)
    return wrapped

# Routes
@routes.post('/v1/images/upload')
async def post_image(request: web.Request):
    req = await request.json()
    urls = req.get('urls', None)
    if urls is None: 
        return web.Response(status=400, text='Bad', reason='Bad Request. No `urls` field.')
    valid, invalid = hf.partition(hf.is_valid_url, urls)
    uploaded = Uploaded(pending=list(valid), failed=list(invalid))
    job = Job(job_id=str(uuid.uuid4()), uploaded=uploaded)
    request.app['jobs'][str(job.job_id)] = job
    handle_job(job)
    return web.Response(text=str(job.job_id))

async def get_status(request: web.Request) -> web.Response:
    job_id = request.match_info.get('job_id', None)
    job = request.app['jobs'].get(job_id, None)
    if job is None:
        return web.Response(text=f'Job {job_id} was not found.')
    return web.Response(text=str(job))

@routes.get('/v1/images')
async def get_images(request: web.Request) -> web.Response:
    return web.Response(text='hello')
    
@background
async def handle_job(job: Job) -> None:
    import time
    pending, completed, failed = astuple(job.uploaded)
    job.status = InProgress()
    for url in pending:
        try:
            image = hf.download_image(url)
        except Exception as e:
            print(f'Failed: {url}')
            failed.append(url)
            job.uploaded = replace(job.uploaded, pending=hf.tail(pending), failed=failed)
        else:
            print(f'Success: {url}')
            completed.append(url)
            job.uploaded = replace(job.uploaded, pending=hf.tail(pending), completed=completed)
    job.finished = dt.datetime.utcnow().isoformat()
    job.status = Complete()

def process_url(url: str):
    pass
    # time.sleep(10)
    # print('done sleeping')

def _upload_to_imgur(self, image_as_b64: str) -> requests.Response:
    """Given a base 64 string, upload it as an image to Imgur."""
    url = 'https://api.imgur.com/3/image'
    try:
        base64.b64decode(image_as_b64, validate=True)
    except base64.binascii.Error:
        msg = 'image_as_b64 needs to be a valid base-64 string.'
        raise ValueError(msg)
    data = {'image': image_as_b64}
    headers = {'Authorization': f'Client-ID {os.environ["CLIENT_ID"]}'}
    resp = hf.make_request('POST', url, headers=headers, data=data)
    return resp

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    app = web.Application()
    app.add_routes(routes)
    app['jobs'] = dict()
    web.run_app(app, host=host, port=port)
    # asyncio.run(main(address, port))
