#!/bin/bash
#
# docker-entrypoint.sh
#
# A simple Docker entrypoint script that can be used to
# collect static files and run any unapplied migrations
# before starting the Django development server.
#

if [ "$SKIP_ALL" ]
then
    SKIP_REQUIREMENTS_CHECK=1
    SKIP_CONFIGURATION=1
    SKIP_DJANGO_COLLECTSTATIC=1
    SKIP_DJANGO_MIGRATE=1
fi

if [ -z "$SKIP_REQUIREMENTS_CHECK" ]
then
    pip install --upgrade -r requirements.txt
fi

if [ -z "$SKIP_CONFIGURATION" ]
then
    cp ./config/docker-compose/* config/
fi

if [ -z "$SKIP_DJANGO_COLLECTSTATIC" ]
then
    python manage.py collectstatic --noinput
fi

if [ -z "$SKIP_DJANGO_MIGRATE" ]
then
    python manage.py migrate --noinput
fi

exec "$@"
