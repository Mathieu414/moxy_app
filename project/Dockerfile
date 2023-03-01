FROM python:3.9-slim-buster

LABEL maintainer "Mathieu Perrin, mathieu.perrin.co@outlook.fr"

# set working directory in container
WORKDIR /usr/src/app

# Copy and install packages
COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Copy app folder to app folder in container
COPY /app /usr/src/app/

CMD ["python3", "app.py"]