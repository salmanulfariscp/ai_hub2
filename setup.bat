@echo off
REM One-time setup for Windows. Double-click or run:  setup.bat
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
python manage.py makemigrations accounts tools favorites reviews submissions
python manage.py migrate
python manage.py seed_data
echo.
echo Setup finished. Next:
echo   venv\Scripts\activate
echo   python manage.py createsuperuser
echo   python manage.py runserver
pause
