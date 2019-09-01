import asyncio
from aiohttp import web
import itertools
import requests
from functools import wraps

from dataclasses import replace, astuple
from my_types import *
import helpers as hf

def background(func: Func) -> Func:
    @wraps(func)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, func, *args, **kwargs)
    return wrapped

# Routes
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

async def get_images(request: web.Request) -> web.Response:
    return web.Response(text='hello')
    
@background
def handle_job(job: Job) -> None:
    import time
    pending, completed, failed = astuple(job.uploaded)
    job.status = InProgress()
    for url in pending:
        try:
            resp = hf.download_image(url)
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
    # time.sleep(10)
    # print('done sleeping')

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8000
    app = web.Application()
    app.add_routes([web.post('/v1/images/upload', post_image),
                    web.get('/v1/images/upload/{job_id}', get_status),
                    web.get('/v1/images', get_images)])
    app['jobs'] = dict()
    web.run_app(app, host=host, port=port)
    # asyncio.run(main(address, port))
