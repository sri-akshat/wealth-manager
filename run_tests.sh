#!/bin/bash

# Exit on error
set -e

# Activate virtual environment
source .venv/bin/activate

# Array of services with coverage requirements
services_with_coverage=(
    "user-service"
    "investment-service"
)

# Array of services without coverage requirements
services_without_coverage=(
    "admin-service"
    "kyc-service"
    "notification-service"
    "transaction-service"
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Initialize counters
passed=0
failed=0

# Set environment variables for testing
export TEST_MODE=True
export TESTING=True

# Run tests for services with coverage requirements
for service in "${services_with_coverage[@]}"; do
    echo -e "\n${GREEN}Running tests for $service (with coverage requirements)...${NC}\n"
    
    # Change to service directory
    cd "services/$service" || continue
    
    # Set PYTHONPATH to include service source, shared utilities, and current directory
    export PYTHONPATH="$PWD/src:$PWD/../../services/shared:$PYTHONPATH"
    
    # Run pytest with coverage requirements
    if pytest tests/ \
        -v \
        --cov=src \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        --import-mode=importlib; then
        ((passed++))
    else
        ((failed++))
    fi
    
    # Return to root directory
    cd ../..
done

# Run tests for services without coverage requirements
for service in "${services_without_coverage[@]}"; do
    echo -e "\n${GREEN}Running tests for $service (without coverage requirements)...${NC}\n"
    
    # Change to service directory
    cd "services/$service" || continue
    
    # Set PYTHONPATH to include service source, shared utilities, and current directory
    export PYTHONPATH="$PWD/src:$PWD/../../services/shared:$PYTHONPATH"
    
    # Run pytest without coverage requirements
    if pytest tests/ \
        -v \
        --import-mode=importlib; then
        ((passed++))
    else
        ((failed++))
    fi
    
    # Return to root directory
    cd ../..
done

# Print summary
echo -e "\n${GREEN}Test Summary:${NC}"
echo -e "Passed: ${GREEN}$passed${NC}"
echo -e "Failed: ${RED}$failed${NC}"

# Exit with failure if any tests failed
[ "$failed" -eq 0 ] 