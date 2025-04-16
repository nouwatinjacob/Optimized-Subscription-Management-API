# Use the official Python image from the DockerHub
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the local code to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Expose the port Flask will run on
EXPOSE 5000

# Command to run migrations and start the app
CMD ["sh", "-c", "flask db upgrade && flask run --host=0.0.0.0"]
