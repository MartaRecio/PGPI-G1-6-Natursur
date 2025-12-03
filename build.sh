#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd natursur
python manage.py collectstatic --no-input

# 1. Crear migraciones para home
python manage.py makemigrations home --noinput

# 2. Aplicar TODAS las migraciones
python manage.py migrate --noinput