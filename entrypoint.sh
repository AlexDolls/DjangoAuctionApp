python3 manage.py flush --no-input
python3 manage.py makemigrations
python3 manage.py migrate
exec "$@"
