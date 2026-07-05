#!/bin/bash

# --- CONFIGURATION ---
PROJECT_NAME="nwtimetracking"
PROJECT_VERSION="6.0.1"
PROJECT_ALIAS="nwtime"
CLI_NAME="nwtimetrackingcli"

COMPANY_NAME="numbworks"
COPYRIGHT="numbworks"
TRADEMARK="numbworks"
FILE_DESCRIPTION="A CLI application that can run several automated data analysis tasks on a time tracking file and save the results as a PDF report."

DOCKER_FILE="nwtimetrackingcli-dockerfile"
BASE_IMAGE="python:3.12.5-bookworm"

# --- DOCKER IMAGE CHECK ---
if [[ "$(docker images -q $BASE_IMAGE 2> /dev/null)" == "" ]]; then
    docker pull $BASE_IMAGE
fi

# --- BUILD COMMAND ---
time DOCKER_BUILDKIT=1 docker build --progress=plain \
  -f "$DOCKER_FILE" \
  --build-arg PROJECT_NAME="$PROJECT_NAME" \
  --build-arg PROJECT_VERSION="$PROJECT_VERSION" \
  --build-arg PROJECT_ALIAS="$PROJECT_ALIAS" \
  --build-arg CLI_NAME="$CLI_NAME" \
  --build-arg COMPANY_NAME="$COMPANY_NAME" \
  --build-arg COPYRIGHT="$COPYRIGHT" \
  --build-arg TRADEMARK="$TRADEMARK" \
  --build-arg FILE_DESCRIPTION="$FILE_DESCRIPTION" \
  --output . .