FROM python:3.7-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt

RUN pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local
COPY src /src


ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "src/app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

EXPOSE 5000

CMD flask run --host=0.0.0.0
