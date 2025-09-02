web: sh -c "python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT"
worker: python manage.py rqworker default