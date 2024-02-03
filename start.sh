#!/bin/bash

if [[ -z "${DEVELOP}" ]]; then
    echo "starting gunicorn"
    gunicorn semantic_kraus_api.main:app -w 4 --timeout=200 --threads=4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000
fi
