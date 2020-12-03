#!/bin/bash

PYTHONPATH=. alembic -c migrations/alembic.ini upgrade head
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
