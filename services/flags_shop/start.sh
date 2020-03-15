#!/bin/bash

set -e

sleep 5
python init_db.py

## uncomment for simple deploy
#python main.py

gunicorn main:app_wrapper --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornUVLoopWebWorker --workers 3
