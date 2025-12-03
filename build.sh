#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd natursur
python manage.py collectstatic --no-input

# 1. MIGRAR home PRIMERO (crea home_user)
python manage.py migrate home --noinput

# 2. LUEGO migrar todo lo demás
python manage.py migrate --noinput