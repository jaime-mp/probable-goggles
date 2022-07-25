<!-- Build the image -->
docker build .
<!-- Raise Docker Compose services. -->
docker-compose up
<!-- Run flake8 inside container. -->
docker-compose run --rm app sh -c "flake8"
<!-- Starting a Django app.  -->
docker-compose run --rm app sh -c "django-admin startapp [appname]"
<!-- Execute a manage.py command. -->
docker-compose run --rm app sh -c "python manage.py [command]"
