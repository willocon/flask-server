FROM python:3.13

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv
WORKDIR /app
COPY . .
RUN pipenv install --system
RUN mkdir -p /logs
CMD gunicorn app:app -b 0.0.0.0:8080 --timeout 5 --workers 1 --threads 4