FROM python:3.10.4-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add gcc python3-dev build-base linux-headers pcre-dev

WORKDIR /usr/app
RUN addgroup -S launcher && adduser -S launcher -G launcher -D -u 101
ADD public /usr/app/public
RUN chown -R 101:launcher /usr/app/public
RUN ls /usr/app -ln

USER 101

ENV TZ=Europe/Berlin

ADD requirements.txt .
RUN pip install --user -r requirements.txt

ADD flask_templates /usr/app/flask_templates
ADD app.py /usr/app/app.py
ADD config.py /usr/app/config.py

CMD ["/home/launcher/.local/bin/uwsgi", "--http",  "0.0.0.0:5000", "--module", "app:app", "--uid", "101", "--enable-threads"]
