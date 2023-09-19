FROM continuumio/miniconda3

# Set working directory
WORKDIR /app/src 

RUN apt-get update && apt-get install -y gdal-bin libgdal-dev g++

# Copy environment.yaml
COPY environment.yaml /app/environment.yaml

# Create conda environment
RUN conda env create -f /app/environment.yaml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "clearvote", "/bin/bash", "-c"]

# Set PYTHONPATH
ENV PYTHONPATH /app

# Copy the entire src directory:
COPY ./src /app/src

# Set the command to run your application:
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "clearvote", "python", "clearvote.py"]
