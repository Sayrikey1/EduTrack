# Dockerfile
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# RUN apt-get update && \
#     apt-get install -y build-essential libpq-dev && \
#     rm -rf /var/lib/apt/lists/*
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*


# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Entrypoint
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
