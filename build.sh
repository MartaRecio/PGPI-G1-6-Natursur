#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd natursur
python manage.py collectstatic --no-input

# Core Django primero
python manage.py migrate auth --noinput
python manage.py migrate contenttypes --noinput
python manage.py migrate admin --noinput
python manage.py migrate sessions --noinput

# Resetear home completamente
python manage.py migrate home zero --noinput 2>/dev/null || true
python manage.py makemigrations home --noinput 2>/dev/null || true
python manage.py migrate home --noinput

# Final
python manage.py migrate --noinput