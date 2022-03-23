FROM python:3.10.3-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD flask_templates /usr/app/flask_templates
ADD public /usr/app/public
ADD app.py /usr/app/app.py

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
