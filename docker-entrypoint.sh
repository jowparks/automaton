#!/bin/bash

# Start Gunicorn processes
export DJANGO_SETTINGS_MODULE=automaton.settings.docker
echo Starting Gunicorn.
exec gunicorn automaton.wsgi:application \
    --bind 0.0.0.0:8000 \
    --timeout $GUNICORN_TIMEOUT \
    --workers 3