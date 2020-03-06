#!/bin/bash

python init_db.py

## uncomment for simple deploy
#python main.py

gunicorn main:gunicorn_app --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornUVLoopWebWorker