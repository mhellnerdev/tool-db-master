# pull container from docker hub
FROM python:alpine

# set docker OS level env variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=run.py

# apt install required OS dependencies that allow gcc to compile the python package requirements correctly
RUN apk update && apk add gcc libc-dev make git libffi-dev openssl-dev python3-dev libxml2-dev libxslt-dev

# DEPRECATED. Cannot install authbind on the python3 alpine OS container.
# install and setup authbind to allow container to be exposed on port 80 without sudo
# RUN apk add authbind
# RUN touch /etc/authbind/byport/80 && chmod 500 /etc/authbind/byport/80 %% chown USER /etc/authbind/byport/80

# DEPRECATED. Does not work either.
# use of iptables to route 80 to 5000 on the container
# RUN apk install iptables
# RUN iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

# using ufw to open port 80 http
RUN apk add ufw
RUN ufw allow http

# create folder on container os for flask app to live
RUN mkdir /tooldb

# define working dir for docker to use for copy processes
WORKDIR /tooldb

# copy python package dependency file
COPY requirements.txt /tooldb/

# use pip to install packages on container os that are defined in the requirements.txt
RUN pip install -r requirements.txt

# copy contents of . or local hosts folder to the WORKDIR on the container
COPY . /tooldb/

# next line has been commented out, use this command to run in development mode
# CMD python run.py 

# run bash script to start PRODUCTION Flask server via UWSGI/gunicorn production engine
CMD ./gunicorn.sh


#### NOTES ####
# this file is currently setup to run the bash script ./gunicorn.sh. this launches the flask server with multi thread workers to handle requests. with out this you cannot have concurrent http requests.

# docker command to run container mapping to http port and passing environment variable for debug mode true.
# this is to be used only when running in development mode
# docker run -p 80:<port defined in app.run> -e DEBUG=1 <image name>