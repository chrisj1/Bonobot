FROM python:3.14-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Pull the application code into the container
COPY . .

# Pull in GCC, et. al if we need it for C-extensions
# Install build dependencies, install Python packages, then clean up to reduce image size
RUN apt-get update && apt-get -y install build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential \
    && rm -rf /var/lib/apt/lists/*
# Start the bot
CMD ["python3", "main.py"]
