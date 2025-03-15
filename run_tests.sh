#!/bin/bash

# Exit on error
set -e

# Set up Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Install test dependencies
pip install -r requirements-test.txt

# Generate OpenAPI specifications
echo "Generating OpenAPI specifications..."
python scripts/generate_openapi.py

# Run OpenAPI compliance tests
echo "Running OpenAPI compliance tests..."
python -m pytest scripts/test_openapi_compliance.py -v

# Run service-specific tests
echo "Running service tests..."

# Define services and their coverage requirements
services="user-service investment-service"
coverage_requirement=80

# Run tests for each service
for service in $services; do
    echo "Testing $service (required coverage: $coverage_requirement%)..."
    cd "services/$service"
    
    # Install service package in development mode
    pip install -e .
    
    # Run tests with coverage
    pytest --maxfail=1 \
           --disable-warnings \
           --cov=src \
           --cov-report=xml \
           --cov-report=term-missing \
           --junitxml=junit.xml \
           -o junit_family=legacy \
           tests/
    
    # Check coverage
    coverage_result=$(coverage report | grep TOTAL | awk '{print $NF}' | sed 's/%//')
    if (( $(echo "$coverage_result < $coverage_requirement" | bc -l) )); then
        echo "Error: Coverage for $service is $coverage_result%, which is below the required $coverage_requirement%"
        exit 1
    fi
    
    cd ../..
done

echo "All tests passed successfully!" 