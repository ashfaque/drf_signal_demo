#!/bin/sh

PYTHON_INTERPRETER="/path_to_python_env/env/bin/python3"
DJANGO_APP_DIR="/path_to_project_root_dir/drf_signal_simplejwt"
DJANGO_PORT="8000"

PRIVATE_KEY_PATH="/path_to/domain_com_private.pem"
CERT_KEY_PATH="/path_to/domain_com_crt.pem"

CPU_COUNT=4

cd $DJANGO_APP_DIR
# $PYTHON_INTERPRETER -m uvicorn drf_signal_simplejwt.asgi:application --host 0.0.0.0 --port $DJANGO_PORT --workers $(($CPU_COUNT * 2 + 1))
$PYTHON_INTERPRETER -m uvicorn drf_signal_simplejwt.asgi:application --host 0.0.0.0 --port $DJANGO_PORT --ssl-keyfile $PRIVATE_KEY_PATH --ssl-certfile $CERT_KEY_PATH --workers $(($CPU_COUNT * 2 + 1))
