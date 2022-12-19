### Dockerfile to build the UP42 block.

# Use a standard python image as a base
FROM python:3.8-slim

RUN apt-get update && \
    apt-get install --no-install-recommends --yes build-essential g++

ARG BUILD_DIR=.

# The manifest file contains metadata for correctly building and
# tagging the Docker image. This is a build time argument.
ARG manifest
LABEL "up42_manifest"=$manifest

# Working directory setup.
WORKDIR /block
COPY $BUILD_DIR/requirements.txt /block

# Install the Python requirements.
RUN pip install -r requirements.txt

# Copy the code into the container.
COPY $BUILD_DIR/src /block/src

# Invoke run.py.
CMD ["python", "/block/src/run.py"]
