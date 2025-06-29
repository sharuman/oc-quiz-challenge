# Engineering Assessment

Starter project to use for the engineering assessment exercise

## Requirements
- Docker
- docker compose

## Tech Stack
- Django
- DRF
- Docker + docker-compose
- DevContainer (VS Code)

## Getting started
Build the docker container and run the container for the first time
```docker compose up```

Rebuild the container after adding any new packages
``` docker compose up --build```

Setup .env file based on the example .env file
1. `cp .env.example .env`
2. set `.env` file accordingly

The run command script creates a super-user with username & password picked from `.env` file

# Run
The following commands have been tested from devcontainer in VSC
1. `python manage.py makemigrations`
2. `python manage.py migrate`
3. `python manage.py seed_database` (optional)
4. `python manage.py runserver 0.0.0.0:8001`
5. `python manage.py test` (optional)

## API Documentation
Accessible at `/api/docs/`.

# NOTES
- Multiple concurrent sessions are not supported --> Only oner pair of token per user
- User cannot change the answers