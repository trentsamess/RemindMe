#!/bin/bash

set -e

show_help() {
    echo """
Usage: docker run <imagename> COMMAND
Commands
dev     : Start a normal Django development server.
lint    : Run lints.
manage  : Start manage.py
prod    : Run wsgi server.
help    : Show this message
"""
}

prepare() {
    until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do sleep 1; done;
}

# Run
case "$1" in
    dev)
        prepare
        python3 manage.py runserver 0.0.0.0:8000
    ;;
    prod)
        prepare
        uwsgi --ini uwsgi.ini
    ;;
    celery)
        prepare
        celery -A remindme worker
    ;;
    manage)
        python3 manage.py "${@:2}"
    ;;
    test)
        prepare
        make test
    ;;
    lint)
        make lint
    ;;
    help)
        show_help
    ;;
    *)
        "$@"
    ;;
esac
