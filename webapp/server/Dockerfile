# Use an official Python runtime as base image
FROM python:3.9.6

# Set working directory
WORKDIR /app/src

# Install system dependencies
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev g++

# Copy requirements.txt
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set PYTHONPATH
ENV PYTHONPATH /app

# Copy the entire src directory
COPY ./src /app/src

# Set the command to run your application:
CMD ["python", "clearvote.py"]