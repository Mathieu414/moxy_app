FROM python:3.11.10-bullseye

LABEL maintainer "Mathieu Perrin, mathieu.perrin.co@outlook.fr"

# set working directory in container
WORKDIR /usr/src/app

RUN apt-get update \
    && apt-get install -y \
    texlive-full

# Copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy app folder to app folder in container
COPY /app /usr/src/app/

# Production settings using gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:server