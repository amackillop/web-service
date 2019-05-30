import argparse
import datetime as dt
import inspect
import sys

from flask import Flask
from flask_restful import Resource, Api, reqparse, inputs

from job_handler import JobHandler

import logging
logging.basicConfig(filename='logs/log.log', level=logging.DEBUG, filemode='w')

class Images(Resource):

    # Defined endpoints for this resource.
    URLs = ('/v1/images/',)

    def __init__(self, job_handler):
        self.job_handler = job_handler

    def get(self):
        return {'uploaded': self.job_handler.images}


class Jobs(Resource):

    # Defined endpoints for this resource.
    URLs = ('/v1/images/upload/', '/v1/images/upload/<job_id>')

    parser = reqparse.RequestParser()
    parser.add_argument('urls', type=inputs.url, action='append')

    def __init__(self, job_handler: JobHandler):
        """Initialize the resource with a JobHandler instance.

        The job handler does the background processing and manages the state 
        of the API.
        
        """
        self.job_handler = job_handler

    def get(self, job_id: str) -> dict:
        """Get the status of a particular job.
        
        Endpoint: /v1/images/upload/:job_id
        
        """
        return self.job_handler.jobs.get(job_id, f'Job does not exist: {job_id}')

    def post(self):
        """ Post a job to this api. A job consists of an array of image URLs.
        
        Endpoint: /v1/images/upload/

        Example request body:
        {
            "urls": [
                "https://farm3.staticflickr.com/2879/11234651086_681b3c2c00_b_d.jpg",
                "https://farm4.staticflickr.com/3790/11244125445_3c2f32cd83_k_d.jpg"
            ]
        }

        """
        urls = self.parser.parse_args()['urls']
        job = self.job_handler.submit(urls)
        return {'jobId': job['id']}
        

def main(client_id, num_threads, conc_reqs):
    app = Flask(__name__)
    api = Api(app)

    # This collects the defined resources automatically as new ones are defined.
    resources = ((obj, obj.URLs) for _, obj in 
                inspect.getmembers(sys.modules[__name__], inspect.isclass)
                if obj.__module__ is __name__)

    job_handler = JobHandler(client_id, num_threads, conc_reqs)
    for resource, urls in resources:
        api.add_resource(resource, *urls, resource_class_args=(job_handler,))

    app.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    # TODO: Implement argparse for passing these through the command line.
    client_id = '96e2154893e4610'
    num_threads = 2
    conc_reqs = 3

    main(client_id, num_threads, conc_reqs)