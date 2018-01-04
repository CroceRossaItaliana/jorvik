#!/bin/bash
#
# docker-entrypoint.sh
#
# A simple Docker entrypoint script that can be used to
# collect static files and run any unapplied migrations
# before starting the Django development server.
#

pip install --upgrade -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

exec "$@"
