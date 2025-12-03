#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

cd natursur

python manage.py collectstatic --no-input

# Solo este comando para limpiar el error
echo "TRUNCATE django_content_type CASCADE;" | python manage.py dbshell 2>/dev/null || true

python manage.py migrate --noinput