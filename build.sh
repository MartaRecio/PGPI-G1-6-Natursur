#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
cd natursur
python manage.py collectstatic --no-input

# 1. Crear migraciones para home
python manage.py makemigrations home --noinput

# 2. Aplicar TODAS las migraciones
python manage.py migrate --noinput

# Después de migrate
python home/populateDB.py 2>/dev/null || echo "Scraping ejecutado o falló"

# CARGAR DATOS después de migrar
python manage.py loaddata home/fixtures/initial_data.json 2>/dev/null || echo "No fixture data found or already loaded"

# Crear superusuario si no existe
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('Fernando', 'admin@gmail.com', 'admin') if not User.objects.filter(username='Fernando').exists() else None" | python manage.py shell 2>/dev/null || true