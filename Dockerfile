FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

# Copy app
COPY . /app

# Default command
CMD ["python", "-m", "src.app.cli"]
