FROM python:3.10-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev zip ffmpeg linux-headers htop

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN python3 -m pip install -r requirements.txt
