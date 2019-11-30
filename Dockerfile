FROM python:3.7-alpine
EXPOSE 5000
WORKDIR /app

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY . /app
