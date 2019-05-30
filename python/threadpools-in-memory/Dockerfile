FROM python:3.7-alpine as base

FROM base as builder
RUN mkdir /install
WORKDIR /install
RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY src /src
COPY logs /logs

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "/src/app.py"
ENV FLASK_ENV "production"
ENV FLASK_DEBUG False

EXPOSE 5000
CMD python src/app.py 
# CMD flask run --host=0.0.0.0
