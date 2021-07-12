FROM python:3.9.6-slim-buster

# Setting PYTHONUNBUFFERED to a non empty value ensures that the python output is sent straight to terminal (e.g. your container log) 
# without being first buffered and that you can see the output of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED 1

RUN apk update \
	&& apk add build-base

RUN mkdir /code
	
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

