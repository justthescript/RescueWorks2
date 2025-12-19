web: cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 4 wsgi:application
release: cd backend && python manage.py migrate
