FROM python:3.8.10-alpine
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py
RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev 
RUN mkdir /tooldb
WORKDIR /tooldb
COPY requirements.txt /tooldb/
RUN pip install -r requirements.txt
COPY . /tooldb/
# CMD python run.py # use this command to run in development mode
CMD gunicorn --bind 0.0.0.0:5000 -w 3 run:app


# docker command to run gunicorn container
# this exposes port 80 to the localhost's web browser on the defined port (5000) from the container engine
# docker run -p 80:5000 -e DEBUG=0 flask_app_dev
