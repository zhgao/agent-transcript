#!/bin/sh
set -e
pip install --no-cache-dir -r /srv/app/requirements.txt
cd /srv
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
