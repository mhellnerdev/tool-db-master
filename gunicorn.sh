#!/bin/sh
gunicorn --chdir tooldb tooldb:tooldb -w 2 --threads 2 -b 0.0.0.0:80