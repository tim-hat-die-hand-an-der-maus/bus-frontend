FROM python:3.10.3-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add gcc python3-dev build-base linux-headers pcre-dev

WORKDIR /usr/app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD flask_templates /usr/app/flask_templates
ADD public /usr/app/public
ADD app.py /usr/app/app.py
ADD config.py /usr/app/config.py

ENV TZ=Europe/Berlin

RUN addgroup -S launcher && adduser -S launcher -G launcher -D -H -u 101
USER 101

CMD ["uwsgi", "--http",  "0.0.0.0:5000", "--module", "app:app", "--uid", "101", "--enable-threads"]
