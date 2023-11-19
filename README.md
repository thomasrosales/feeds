# Feeds For Sendcloud

Sendcloud interview project

# Table of contents
1. [Requirements](#requirements)
2. [Business decisions](#business-decisions)
3. [Documentation](#documentation)
   1. [How to recreate the retry mechanism scenario](#how-to-recreate-the-retry-mechanism-scenario)
   2. [How to recreate the force update scenario](#how-to-recreate-the-force-update-scenario)
4. [Docker](#docker)
5. [Local Deployment](#local-deployment)
6. [Settings](#settings)
7. [Basic Commands](#basic-commands)
   1. [Setting Up Your Users](#setting-up-your-users)
   2. [Running Django App](#running-django-app)
   3. [Getting Basic Authentication](#getting-basic-authentication)
   4. [Running Django Shell](#running-django-shell)
   5. [Running Pytest](#running-pytest)
   6. [Running Coverage](#running-coverage)
   7. [Running Type Checks](#running-type-checks)
   8. [Running Celery](#running-celery)
8. [Improvements](#improvements)

## Requirements

Have installed:

- Python >= 3.9
- Poetry >= 1.7.0
- Docker or Docker Desktop >= 24.0.6
- Postgres (you can use a docker container or the dockerized solution) >= 13.5 (for local deployment the author recommends had Postgres installed)

## Business decisions

During the implementation of the solution for the Feeds application the author decided the followings business rules or definitions for the project:

- All users must be authenticated to use the service.
  - The authentication selected for the application is BasicAuthentication. Basic authentication requires the header `Authorization: Basic token`. [Here](#getting-basic-authentication)
- If you want to create/update/remove a Feed you must be admin user or has admin site access. To do it you need to create a superuser using django commands. [Here](#setting-up-your-users).
  - There are 3 fields you cannot update through API: `last_refresh`, `state`, and `source_err` because they are part of the async update posts process
- If you want to force the update process on a Feed you must follow the Feed first.
- If you want to mark as read/unread a post you must follow the Feed first.
- If you want to see a specific Posts you must follow the Feed first.
- If you followed a Feed and you have marked as read some Posts and you decided to unfollow the Feed then the posts read marks remains, although you can't filter or access to the posts till you start following again the Feed.
- The author decided to use Django instead of FastAPI.
- Test cases were added to the `tests/` folder. There is still work to do regarding test cases, the author has covered the most important cases.
- Celery was configured to run whit two workers and one main process.

## Documentation

- It was provided the following path to get the API documentation using swagger: http://localhost:8000/api/docs/
- It was provided the following path to use the admin site: http://localhost:8000/admin/
- It was provided the following path to use the Flower service monitor for celery: http://localhost:5555/
- If you select the docker solution to run the application you will count with the following preloaded data. You can also run it locally [command](#setting-up-your-users):

    | Username 	   | Password 	 | Admin site access 	 |
    |--------------|------------|---------------------|
    | root     	   | root     	 | yes              	  |
    | staff    	   | staff    	 | no               	  |
    | staff2   	   | staff2   	 | no               	  |

    | Feed                                        	 | Posts 	 | Next Execution                	 |
    |-----------------------------------------------|---------|---------------------------------|
    | https://www.clarin.com/rss/lo-ultimo/       	 | 0     	 | 2 minutes from docker started 	 |
    | http://www.nu.nl/rss/Algemeen               	 | 0     	 | 2 minutes from docker started 	 |
    | https://feeds.feedburner.com/tweakers/mixed 	 | 0     	 | 2 minutes from docker started 	 |

### How to recreate the retry mechanism scenario

1. Create a feed with a wrong source type (a wrong source is a website that returns something different to a rss xml):
   ```bash
   curl -H "Accept: application/json" -H "Authorization: Basic <AUTH_USER_TOKEN>" -X POST -d '{"source": "https://.../curl-post-json-example"}' http://localhost:8000/api/feeds/
   ```
   - After the feed creation a task is triggered to get all post related to that feed source, due to is a wrong RSS XML, the process will fail and marked as failed
   - The workaround is to update the Feed `state` to "updated" and the `last_refresh` field to a date in the past (between 1 and 5 minutes ago since you performed this step) through admin site.
   - Once you save it, the async update process will take this Feed to start adding the new posts if it has at last one, however, due to the feed source is invalid the process will fail and will trigger the retry mechanism.

2. Other solution may be to disconnect your internet when the application is running normally, this will produce every update post process of each Feed failed due to HTTP error connection, producing the retry mechanism trigger.

### How to recreate the force update scenario

1. Create a feed with a wrong source type (a wrong source is a website that returns something different to a rss xml):
   ```bash
   curl -H "Accept: application/json" -H "Authorization: Basic <AUTH_USER_TOKEN>" -X POST -d '{"source": "https://.../curl-post-json-example"}' http://localhost:8000/api/feeds/
   ```
   - After the feed creation a task is triggered to get all post related to that feed source, due to is a wrong RSS XML, the process will fail and marked as failed
   - Make sure you are following the feed for force update process:
     ```bash
     curl -H "Accept: application/json" -H "Authorization: Basic <AUTH_USER_TOKEN>" -X POST http://localhost:8000/api/feeds/<FEED_ID>/follow-me/
     ```
   - Update the source feed with a valid one:
     ```bash
     curl -H "Accept: application/json" -H "Authorization: Basic <AUTH_USER_TOKEN>" -X PATCH -d '{"source": "http://valid-source/rss"}' http://localhost:8000/api/feeds/<FEED_ID>/
     ```
   - Force the update process:
     ```bash
     curl -H "Accept: application/json" -H "Authorization: Basic <AUTH_USER_TOKEN>" -X POST http://localhost:8000/api/feeds/<FEED_ID>/force-update/
     ```

## Docker

For this project were created a docker-compose.yml to deploy all infrastructure that application needs. The docker compose is a specification to tell docker how to create and deploy the new infrastructure for the application, such us, database services, redis, celery, the application itself, etc.

Requirements:

- Had Docker installed. [Here](https://docs.docker.com/engine/install/).

1. Execute the next command to build and run the application infrastructure:

    ```bash
    cd <PROJECT_PATH>/feeds/
    docker-compose up --build -d
    ```

2. Start and stop application when you need:

    ```bash
    docker-compose stop|start
    ```
3. Remove all infrastructure:

    ```bash
    docker-compose down
    ```
4. If you need just some services to run the application locally the author added a special docker-compose called docker-compose-local.yml that just creates the postgres and redis services:

    ```bash
    docker-compose -f ./docker/docker-compose-local.yml up --build -d
    ```

## Local Deployment

Go to a terminal to your projects path and clone this project:

```bash
cd ./<PROJECT_PATH>/
git clone https://github.com/thomasrosales/feeds.git
```

From here you should always work in the feeds/ directory, however you must install python project dependencies to start using it:

```bash
cd /feeds
poetry install
```

Then you can access to your terminal activating the virtual environment that poetry created for you:
```bash
poetry shell
```

## Settings

Once inside and with the virtual environment activated:

- To load your local environment variable .env you must set the following global environment variable. This is going to tell django to load the .env file. 
    ```bash
    set DJANGO_READ_DOT_ENV_FILE=True
    ```
- Use the .env.example file to load the environment variables, remember to create a new file under the name to .env
    ```bash
    copy .env.example .env
    ```
- You now have prepared all necessary to run the Django application, but you need first run the [migrations process.](https://docs.djangoproject.com/en/4.2/topics/migrations/) The migration process allows you to create the database Tables for each apps in the Django application:
    ```bash
    python manager.py migrate
    ```
- And then you should execute the next command to have all admin service statics available and working
    ```bash
    python manager.py collectstatic
    ```
  
Now you are able to run the django application locally. [Here](#running-django-app). 

## Basic Commands

**Most of the followings commands need the [Settings](#settings) step being done.**

### Setting Up Your Users

- To create a **superuser account**, use this command:
    ```bash
    python manage.py createsuperuser
    ```
- For test purpose a command was added to create 1 superuser, 2 regular users, and 3 Feeds:
    ```bash
    python manage.py create_user_feeds_for_testing_purpose
    ```

### Running Django App
```bash
python manager.py runserver_plus
```

### Getting Basic Authentication

To perform this step the django application must be initialized and migrations run. **[Go here](#settings)**

- To create a *regular user*, go to the admin site where you can create, edit and remove users. Once you have created a user or a superuser you must generate a base64 token to be used as a basic token:
   ```bash
   python manage.py pass_base64 <USER> <PASSWORD>
   ```
   The abode script generates the base64 token, you should see something similar to: 
   ```bash
   Successfully created "YWRtaW46YWRtaW4="
   ```
   This token must be used as Basic Authorization Token inside the request header like this:
    ```bash
    curl -H "Accept: application/json" -H "Authorization: Basic YWRtaW46YWRtaW4=" -X GET http://localhost:8000/api/feeds/
    ```
### Running Django Shell
```bash
python manager.py shell_plus
```

### Running Pytest
```bash
pytest
```

### Running Coverage
```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

### Running Type Checks
```bash
mypy feeds_for_sendcloud
```

### Running Celery

This app comes with Celery and you can run it in your local terminal as standalone.

- To start using Celery you must install Redis as default broker, the author recommends to use docker 
  ```bash
  docker run --name sendcloud-redis -p 6379:6379 -d redis:latest
  ```
- The .env file has an environment variable with the value of a redis url
    ```bash
    cat .env | grep CELERY_BROKER_URL
   ```
- Open a new terminal tab and following the next steps:
    ```bash
    cd ./<project_path>/feeds
    poetry shell
    set DJANGO_READ_DOT_ENV_FILE=True
    celery -A config.celery_app worker -c 2 -l info
    ```
    Celery is gonna running with two concurrency process you can modify it as your wish. Optional: if you are using Windows you must run Celery using [Eventlet](https://eventlet.net/) or [Gevent](https://www.gevent.org/).
    ```bash
    celery -A config.celery_app worker -c 2 -l info -P eventlet
    ```
    Eventlet comes by default when you install poetry dependencies.

- To run periodic task you must run Celery Beat plugin in other new terminal. Celery Beat is a scheduler service:
    ```bash
    cd ./<project_path>/feeds
    poetry shell
    set DJANGO_READ_DOT_ENV_FILE=True
    celery -A config.celery_app beat -l INFO
    ```

## Improvements

1. Add NGNIX in front of Gunicorn Server [Gunicorn + Nginx](https://gunicorn.org/#deployment)
2. More test cases
3. Setting for production environment, like HTTPS, etc
