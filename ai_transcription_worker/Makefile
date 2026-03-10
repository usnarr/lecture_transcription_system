# Makefile

.PHONY: up down restart logs rebuild-worker

.PHONY: help install configure

# Variables
POETRY := poetry
PYTHON := python

# Default target
help:
    @echo Available commands:
    @echo   make install     - Install project dependencies



install:
    $(POETRY) install


# spin up everything (will build once)
up:
    docker-compose up -d

# tear down
down:
    docker-compose down

restart:
    docker-compose down && docker-compose up -d

rebuild-worker:
    docker-compose up  --no-deps --build celery-worker

logs:
    docker-compose logs -f

worker-logs:
    docker-compose logs -f celery-worker