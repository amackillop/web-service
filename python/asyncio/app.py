"""
Image uploading service implemented using asyncio/aiohttp
"""

import asyncio
import datetime as dt
import uuid
from typing import Tuple

import uvloop
from pymonads.either import Either


from aiohttp import web
from aiohttp.client_exceptions import ClientError
from my_types import Job, Uploaded
import helpers as hf

routes = web.RouteTableDef()

# Routes
@routes.post('/v1/images/upload')
async def post_image(request: web.Request) -> web.Response:
    """Post a job"""
    req = await request.json()
    urls = req.get('urls', None)
    if urls is None: 
        return web.Response(status=400, text='Bad', reason='Bad Request. No `urls` field.')
    job_id = str(uuid.uuid4())
    request.app['jobs'][job_id] = _submit_job(job_id, urls)
    return web.Response(text=job_id+'\n')


@routes.get('/v1/images/upload/{job_id}')
async def get_status(request: web.Request) -> web.Response:
    """Check job status"""
    job_id = request.match_info.get('job_id', None)
    job = request.app['jobs'].get(job_id, None)
    if job is None:
        return web.Response(text=f'Job {job_id} was not found.')
    return web.Response(text=str(job))


@routes.get('/v1/images')
async def get_images(request: web.Request) -> web.Response:
    """Get list of uploaded images"""
    return web.Response(text='hello')
    

# Helpers
def _submit_job(job_id: str, urls: list) -> Job:
    valid, invalid = hf.partition(hf.is_valid_url, urls)
    uploaded = Uploaded(pending=list(valid), failed=list(invalid))
    job = Job(job_id=job_id, uploaded=uploaded)
    asyncio.create_task(_handle_job(job))
    return job


async def _handle_job(job: Job) -> None:
    job.status = 'in-progress'
    await asyncio.gather(*[_handle_download(job, url) for url in job.uploaded.pending])
    job.finished = dt.datetime.utcnow().isoformat()
    job.status = 'complete'


async def _handle_download(job: Job, url: str) -> Either:
    # import random
    # await asyncio.sleep(random.random())
    # print('Done: ', job.job_id)
    # return 'cat'
    try:
        image = await hf.download_image(url)
    except (ClientError, IOError) as exc:
        print(f'Failed: {url}')
        print(exc)
        job.uploaded.failed.append(url)
        job.uploaded.pending.remove(url)
        return ''

    print(f'Success: {url}')
    job.uploaded.completed.append(url)
    job.uploaded.pending.remove(url)
    return image


# def _upload_to_imgur(self, image_as_b64: str) -> requests.Response:
#     """Given a base 64 string, upload it as an image to Imgur."""
#     url = 'https://api.imgur.com/3/image'
#     try:
#         base64.b64decode(image_as_b64, validate=True)
#     except base64.binascii.Error:
#         msg = 'image_as_b64 needs to be a valid base-64 string.'
#         raise ValueError(msg)
#     data = {'image': image_as_b64}
#     headers = {'Authorization': f'Client-ID {os.environ["CLIENT_ID"]}'}
#     resp = hf.make_request('POST', url, headers=headers, data=data)
#     return resp


async def start(app: web.Application, host: str, port: int) -> Tuple[web.AppRunner, web.TCPSite]:
    """Start the server"""
    runner = web.AppRunner(app)
    await runner.setup()
    server = web.TCPSite(runner, host, port)
    await server.start()
    return runner


def main() -> None:
    """Entrypoint"""
    uvloop.install()
    host = '0.0.0.0'
    port = 8000
    app = web.Application()
    app.add_routes(routes)
    app['jobs'] = dict()
    loop = asyncio.get_event_loop()
    runner = loop.run_until_complete(start(app, host, port))
    print('======== Running on http://0.0.0.0:8000 ========\n'
          '(Press CTRL+C to quit)')
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(runner.cleanup())


if __name__ == '__main__':
    import tracemalloc
    tracemalloc.start()
    main()
