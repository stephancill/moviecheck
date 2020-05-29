FROM python:3.6-slim-stretch

LABEL MAINTAINER="FirstName LastName <example@domain.com>"

ENV GROUP_ID=1000 \
    USER_ID=1000

WORKDIR /var/www/

RUN pip install pipenv
RUN pipenv run pip freeze > requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

RUN addgroup -g $GROUP_ID www
RUN adduser -D -u $USER_ID -G www www -s /bin/sh

USER www

EXPOSE 8080

CMD [ "gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--worker-class", "sanic.worker.GunicornWorker"]
