#!/bin/bash

pkill -f "uvicorn main:app"

cd "$(dirname "$0")"
uvicorn main:app --reload --port 9000 &
uvicorn main:app --reload --port 9001 &
uvicorn main:app --reload --port 9002 &

nginx -c "$(pwd)/nginx.conf" 