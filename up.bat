@echo off
echo Starting Quizly Docker Environment...
docker-compose up -d --build
echo.
echo Waiting for database to initialize...
timeout /t 10 /nobreak >nul
echo.
echo Running database migrations...
docker-compose exec web python manage.py migrate
echo.
echo Collecting static files...
docker-compose exec web python manage.py collectstatic --noinput
echo.
echo Quizly is now running at:
echo http://localhost:8000
echo.
echo To view logs: docker-compose logs -f web
echo To stop: docker-compose down