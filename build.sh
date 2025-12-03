set -o errexit

# Install dependencies
pip install -r natursur/requirements.txt

# Navigate to Django project
cd /natursur

# Static files
python manage.py collectstatic --no-input

# Apply ALL migrations (Django handles everything)
python manage.py migrate --noinput