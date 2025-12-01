FROM python:3.14-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Pull the application code into the container
COPY . .

# Pull in GCC, et. al if we need it for C-extensions
RUN apt-get update && apt-get -y install build-essential
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python3", "main.py"]
