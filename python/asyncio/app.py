import asyncio
from aiohttp import web
from urllib.parse import urlparse
import itertools
import requests
from functools import wraps


from my_types import *

def background(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if callable(f):
            return loop.run_in_executor(None, f, *args, **kwargs)
        else:
            raise TypeError('Task must be a callable')    
    return wrapped

# Routes
async def post_image(request: web.Request):
    req = await request.json()
    urls = req.get('urls', None)
    if urls is None: 
        return web.Response(status=400, text='Bad', reason='Bad Request. No `urls` field.')
    valid, invalid = partition(is_valid_url, urls)
    uploaded = Uploaded(pending=list(valid), failed=list(invalid))
    job = Job(job_id=str(uuid.uuid4()), uploaded=uploaded)
    request.app['jobs'][str(job.job_id)] = job
    handle_job()
    return web.Response(text=str(job.job_id))

async def get_status(request: web.Request):
    job_id = request.match_info.get('job_id', None)
    if job_id is None:
        return web.Response(text=f'Job {job_id} was not found.')
    job = request.app['jobs'][job_id]
    return web.Response(text=job.created)

async def get_images(request: web.Request):
    return web.Response(text='hello')
    
@background
def handle_job():
    import time
    time.sleep(10)
    print('done sleeping')

# Helpers
def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc, result.path])
    except:
        return False


def partition(predicate: Callable[[T], bool] , iterable: Iterable[T]):
    'Use a predicate to partition entries into false entries and true entries'
    t1, t2 = itertools.tee(iterable)
    return filter(predicate, t1), itertools.filterfalse(predicate, t2)





# App
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
