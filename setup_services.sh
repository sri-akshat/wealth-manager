#!/bin/bash

# Remove old structure if it exists
rm -rf app

# Create base services structure
for service in user-service kyc-service investment-service transaction-service notification-service admin-service gateway; do
    mkdir -p services/$service/{src,tests,config}
    mkdir -p services/$service/src/{api,core,models,schemas}

    # Create necessary files
    touch services/$service/src/__init__.py
    touch services/$service/src/main.py
    touch services/$service/Dockerfile
    touch services/$service/requirements.txt
    touch services/$service/README.md
done

# Create docker-compose.yml at root level
touch docker-compose.yml
