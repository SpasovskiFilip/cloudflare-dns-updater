# syntax=docker/dockerfile:1
FROM python:alpine

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy relevant files into the container
COPY main.py /app
COPY functions.py /app
COPY requirements.txt /app
COPY domains.json /app

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Run the application.
CMD ["python", "main.py"]