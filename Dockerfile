FROM python:3.14-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# The application code into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot
CMD ["python3", "main.py"]