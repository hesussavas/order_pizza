#!/bin/sh

# cd to django working dir
cd moberries_test_assignment

# run migrations
python3 ./manage.py migrate

# run server
python3 ./manage.py runserver 0.0.0.0:8000