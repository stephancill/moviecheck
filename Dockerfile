FROM python:3.6-stretch

LABEL MAINTAINER="Stephan Cilliers <stephanus.cilliers@protonmail.com>"

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN apt-get install gcc

RUN pip install 'pipenv==2018.11.26'
RUN pipenv install --system --ignore-pipfile
RUN pip install gunicorn

EXPOSE 8080

CMD [ "gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--worker-class", "sanic.worker.GunicornWorker"]
