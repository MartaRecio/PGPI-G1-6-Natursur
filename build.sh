#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# First navigate to Django project folder
cd natursur

python manage.py collectstatic --no-input

# Fake all migrations first to avoid table errors
python manage.py migrate --fake --noinput

# Then apply migrations normally
python manage.py migrate --noinput

# Load initial data if exists
python manage.py loaddata home/fixtures/initial_data.json 2>/dev/null || true