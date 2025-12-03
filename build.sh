#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt playwright bs4 lxml
# 1. INSTALAR CHROME PARA PLAYWRIGHT
playwright install chromium
playwright install-deps 2>/dev/null || true


cd natursur
python manage.py collectstatic --no-input

# 2. Crear migraciones para home
python manage.py makemigrations home --noinput

# 3. Aplicar TODAS las migraciones
python manage.py migrate --noinput

# Después de migrate
python home/populateDB.py

# CARGAR DATOS después de migrar
python manage.py loaddata home/fixtures/initial_data.json 2>/dev/null || true

# Crear superusuario si no existe
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('Fernando', 'admin@gmail.com', 'admin') if not User.objects.filter(username='Fernando').exists() else None" | python manage.py shell 2>/dev/null || true