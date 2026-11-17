#!/usr/bin/env bash
# One-time setup for macOS / Linux. Run:  bash setup.sh
set -e
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
python manage.py makemigrations accounts tools favorites reviews submissions
python manage.py migrate
python manage.py seed_data
echo
echo "Setup finished. Next:"
echo "  source venv/bin/activate"
echo "  python manage.py createsuperuser"
echo "  python manage.py runserver"
