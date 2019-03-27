# A Stateful REST API.
This is a simple api that downloads images from the internet and uploads them to Imgur.

## Setup
To run the flask app in a docker container, run:

`bash start.sh`

In order to run locally, install pipenv (if you do not have it already) and use that to build the virtual environment before launching the app.

```pip install pipenv
pipenv install
pipenv shell
python src/spp.py
```

To run the tests cd into the src directory first.
```
cd src
pytest
```
## Endpoints

After starting the application, post jobs to to the following URL:

`http://0.0.0.0:5000/v1/images/upload/`

The body is an array of URLs to download. Example:
```
{
    "urls": [
        "http://www.dummyimage.com/100x100",
        "http://www.dummyimage.com/200x200"
    ]
}
```

Successful post requests will yield a uuid in order to track the progress of the job.
Check the status with the following end point:

`http://0.0.0.0:5000/v1/images/upload/:job_id`

You can see a list of imgur links for all successful uploads by sending a get request to:

`http://0.0.0.0:5000/v1/images/`

### Example curl commands:

POST a job:

```bash
curl -X POST \
-H 'Content-Type: application/json' \
-d '{"urls":["http://www.dummyimage.com/100x100", "http://www.dummyimage.com/200x200"]}' \
http://0.0.0.0:5000/v1/images/upload/
```

Check the status of a job:

`curl http://0.0.0.0:5000/v1/images/upload/<uuid>`

See all Imgur links from successful uploads:

`curl http://0.0.0.0:5000/v1/images/`
