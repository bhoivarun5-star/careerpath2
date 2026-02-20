#!/bin/bash

echo "BUILD START"

# Ensure pip is up to date
python3.12 -m pip install --upgrade pip

# Install dependencies
python3.12 -m pip install -r requirements.txt

# Create static directory if it doesn't exist
mkdir -p staticfiles

# Collect static files
python3.12 manage.py collectstatic --noinput --clear

echo "BUILD END"
