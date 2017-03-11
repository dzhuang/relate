docker-machine start default
REM docker-machine env default
@FOR /f "tokens=*" %%i IN ('docker-machine env default') DO @%%i
python manage.py runserver 0.0.0.0:8000