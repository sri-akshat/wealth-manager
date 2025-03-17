#!/bin/bash

# Script to create template .env files
# Since .env files are excluded from git, this script helps set up
# the initial templates when cloning the repository

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Creating template .env files...${NC}"

# Create root .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wealthdb

# Authentication
JWT_SECRET_KEY=your-dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Testing
TEST_MODE=false

# GitHub Configuration
GITHUB_TOKEN=your-github-token-here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO

# Feature Flags
ENABLE_SWAGGER=true
ENABLE_REDOC=true

# Codecov Token for Coverage Reports
CODECOV_TOKEN=your-codecov-token-here
EOF

echo -e "${GREEN}✓ Created root .env file${NC}"

# Create services/.env file
mkdir -p services
cat > services/.env << EOF
# Common environment variables for all services

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wealthdb

# Authentication
JWT_SECRET_KEY=your-dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Testing
TEST_MODE=false

# Logging
LOG_LEVEL=INFO

# Service URLs (for service-to-service communication)
USER_SERVICE_URL=http://localhost:8002
INVESTMENT_SERVICE_URL=http://localhost:8001
TRANSACTION_SERVICE_URL=http://localhost:8003
KYC_SERVICE_URL=http://localhost:8004
ADMIN_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8006

# API Documentation
ENABLE_SWAGGER=true
ENABLE_REDOC=true

# Service Modes
DEPLOYMENT_MODE=monolith  # Options: monolith, microservices
DEBUG=true

# External Service APIs
MUTUAL_FUND_API_KEY=your_api_key_here
EMAIL_SERVICE_API_KEY=your_api_key_here
EOF

echo -e "${GREEN}✓ Created services/.env file${NC}"

# Create service-specific .env files
SERVICES=("user-service" "investment-service" "transaction-service" "kyc-service" "admin-service" "notification-service")
PORTS=(8002 8001 8003 8004 8005 8006)

for i in "${!SERVICES[@]}"; do
  SERVICE=${SERVICES[$i]}
  PORT=${PORTS[$i]}
  
  # Create directory if it doesn't exist
  mkdir -p "services/$SERVICE"
  
  # Create .env file
  cat > "services/$SERVICE/.env" << EOF
# $SERVICE Specific Configuration

# Service Information
SERVICE_NAME=$SERVICE
SERVICE_PORT=$PORT

# Database Configuration
# Uncomment and use this to override the common DATABASE_URL if needed
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/${SERVICE//-/_}_db

# Inherit common environment variables from ../services/.env
# Don't specify them here unless you want to override
EOF

  echo -e "${GREEN}✓ Created services/$SERVICE/.env file${NC}"
done

echo -e "${YELLOW}NOTE: These are template files. Update with real values for your environment.${NC}"
echo -e "${YELLOW}DO NOT commit files with real secrets to source control.${NC}"

chmod +x scripts/setup_env_templates.sh

echo -e "${BLUE}All template .env files created successfully!${NC}" 