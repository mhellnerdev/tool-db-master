#!/bin/sh

gunicorn --bind 0.0.0.0:80 -w 3 run:app