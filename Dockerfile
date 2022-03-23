FROM python:3.10.2-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV BASEPATH_RECOMMENDATIONS /recommendations

# RUN apk update
RUN apk add gcc python3-dev jpeg-dev zlib-dev musl-dev

WORKDIR /usr/app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD flask_templates /usr/app/flask_templates
ADD app.py /usr/app/app.py

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "5000"]
