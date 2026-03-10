FROM python:3.10-slim

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not create virtual environments in containers
RUN poetry config virtualenvs.create false

# Install dependencies with verbose output for debugging
RUN poetry install --no-root --only main --no-interaction --no-ansi -vvv

# Copy application code
COPY . /app

ENV PYTHONPATH=/app

CMD ["celery", "-A", "src.celery_app", "worker", "-l", "info"]