# Feeds For Sendcloud

Sendcloud interview project

## Requirements

Have installed:

- Python >= 3.9
- Poetry >= 1.7.0
- Docker or Docker Desktop >= 24.0.6
- Postgres (you can use a docker container) >= 13.5 (for local deployment is configured to use SQLLite or Postgres, the author recommends had Postgres installed)


### Docker

### Local Deployment

Go to a terminal to your projects path and clone this project:

      $ cd ./<PROJECT_PATH>/
      $ git clone https://github.com/thomasrosales/feeds.git

From here you should always work in the feeds/ directory, however you must install python project dependencies to start using it:
      
      $ cd /feeds
      $ poetry install

Then you can access to your terminal activating the virtual environment that poetry created for you:
      
      $ poetry shell

## Settings

Once inside and with the virtual environment activated:

- To load your local environment variable .env you must set the following global environment variable. This is going to tell django to load the .env file. 

      $ set DJANGO_READ_DOT_ENV_FILE=True
- Use the .env.example file to load the environment variables, remember to create a new file under the name to .env

      $ copy .env.example .env
- You now have prepared all necessary to run the Django application, but you need first run the [migrations process.](https://docs.djangoproject.com/en/4.2/topics/migrations/) The migration process allows you to create the database Tables for each apps in the Django application:

      $ python manager.py migrate

## Basic Commands

**Most of the followings commands need the [Settings](#settings) step being done.**

### Setting Up Your Users

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

### Running Django App

      $ python manager.py runserver_plus

### Running Django Shell

      $ python manager.py shell_plus

### Running Pytest

      $ pytest

### Running Coverage

      $ coverage run -m pytest
      $ coverage html
      $ open htmlcov/index.html

### Running Type Checks

      $ mypy feeds_for_sendcloud

### Running Celery

This app comes with Celery and you can run it in your local terminal as standalone.

- To start using Celery you must install Redis as default broker, we use docker 

      $ docker run --name sendcloud-redis -p 6379:6379 -d redis:latest
- The .env file has an environment variable with the value of a redis url

      $ cat .env | grep CELERY_BROKER_URL
- Open a new terminal tab and following the next steps:

      $ cd ./<project_path>/feeds
      $ poetry shell
      $ set DJANGO_READ_DOT_ENV_FILE=True
      $ celery -A config.celery_app worker -c 2 -l info

    Celery is gonna running with two concurrency process you can modify it as your wish. Optional: if you are using Windows you must run Celery using [Eventlet](https://eventlet.net/) or [Gevent](https://www.gevent.org/).

      $ celery -A config.celery_app worker -c 2 -l info -P eventlet
    Eventlet comes by default when you install poetry dependencies.

- To run periodic task you must run Celery Beat plugin in other new terminal. Celery Beat is a scheduler service:

      $ cd ./<project_path>/feeds
      $ poetry shell
      $ set DJANGO_READ_DOT_ENV_FILE=True
      $ celery -A config.celery_app beat -l INFO
