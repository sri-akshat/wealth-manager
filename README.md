# wealth-manager

[![Build Status](https://github.com/sri-akshat/wealth-manager/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/sri-akshat/wealth-manager/actions)
[![codecov](https://codecov.io/gh/sri-akshat/wealth-manager/graph/badge.svg?token=78ZRSI3PVO)](https://codecov.io/gh/sri-akshat/wealth-manager)

Scalable SaaS platform for Independent Financial Advisors (IFAs), AMCs, and financial distributors to manage customer investments, KYC compliance, and mutual fund transactions

## Getting Started

### Prerequisites

- Python 3.9+ (minimum supported version)
- pip 21.2.4+ (required for editable installs with pyproject.toml)
- Git
- Docker & Docker Compose (for containerized development)
- PostgreSQL (for local development without Docker)

### Installation

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/sri-akshat/wealth-manager.git
cd wealth-manager

# Set up the project (creates virtual environment)
./project-setup.sh

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies for all services
find . -name "requirements.txt" -exec pip install -r {} \;
pip install -r requirements-test.txt

# Install services in editable mode for development
cd services/user-service && pip install -e . && cd ../..
cd services/investment-service && pip install -e . && cd ../..
```

### Database Setup

#### Option 1: Using Docker (Recommended)

The project includes Docker Compose configuration for PostgreSQL databases:

```bash
# Start PostgreSQL databases
docker-compose up -d user-db investment-db

# The databases will be available at:
# User Database:
# - Host: localhost
# - Port: 5432
# - Username: user
# - Password: password
# - Database: userdb

# Investment Database:
# - Host: localhost
# - Port: 5433
# - Username: user
# - Password: password
# - Database: investmentdb
```

#### Docker Database Management

Once your databases are running, you can manage them with these commands:

```bash
# Check database status
docker-compose ps

# View database logs
docker-compose logs user-db
docker-compose logs investment-db

# Stop databases
docker-compose stop user-db investment-db

# Stop and remove everything
docker-compose down

# Restart databases
docker-compose restart user-db investment-db

# Test database connections
docker exec wealth-manager-user-db-1 psql -U user -d userdb -c "SELECT version();"
docker exec wealth-manager-investment-db-1 psql -U user -d investmentdb -c "SELECT version();"
```



### Environment Variables Setup

The project uses multiple `.env` files to manage environment variables across different components:

#### Setting Up Environment Files

All `.env` files are excluded from git (via `.gitignore`) to prevent accidental commit of secrets. 
Use the provided script to generate template files:

```bash
# Generate all template .env files
./scripts/setup_env_templates.sh
```

#### Structure of Environment Files

1. **Root `.env`**: Project-wide configuration
   - GitHub and Codecov tokens
   - Main API configuration
   - Global settings

2. **`services/.env`**: Common settings for all services
   - Database connection
   - Authentication settings 
   - Inter-service communication URLs
   - Logging configuration

3. **Service-specific `.env` files** (e.g., `services/user-service/.env`):
   - Settings unique to each service
   - Service port numbers
   - Feature flags
   - Service-specific API keys

When a setting exists in multiple files, the most specific one takes precedence 
(service-specific > services > root).

#### Critical Environment Variables

These variables should be updated with your actual values:

| Variable | Location | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Root `.env` | GitHub personal access token for CI/CD |
| `CODECOV_TOKEN` | Root `.env` | Codecov token for test coverage reporting |
| `JWT_SECRET_KEY` | `services/.env` | Secret key for JWT authentication |
| `DATABASE_URL` | `services/.env` | PostgreSQL connection string for user service |
| `INVESTMENT_DATABASE_URL` | `services/.env` | PostgreSQL connection string for investment service |

### Running the Application

There are multiple ways to run the application:

#### 1. Run All Services as a Monolith (Development)

The monolith runs all microservices in a single process, which is useful for development:

```bash
# Make the script executable
chmod +x run_monolith.sh

# Run the monolith
./run_monolith.sh

# The monolith will be available at: http://localhost:8000
# Health check: http://localhost:8000/health
```

#### 2. Run Individual Services

Each service can be run independently:

```bash
# Example: Run the investment service
cd services/investment-service
uvicorn investment_service.main:app --reload --port 8001

# Example: Run the user service
cd services/user-service
uvicorn user_service.main:app --reload --port 8002
```

#### 3. Run with Docker Compose (Full Stack)

For a production-like environment with all services:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# The API gateway will be available at: http://localhost:8000
```

### Running Tests

This project uses pytest for its test suite and Codecov for test coverage reporting.

```bash
# Run all tests with coverage
./run_tests.sh

# Run tests for a specific service
cd services/user-service
pytest --cov=. --cov-report=xml

# Run tests in development mode (SQLite instead of PostgreSQL)
TEST_MODE=true pytest
```

### Environment Variables

Key environment variables for development:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string for user service | `postgresql://user:password@localhost:5432/userdb` |
| `INVESTMENT_DATABASE_URL` | PostgreSQL connection string for investment service | `postgresql://user:password@localhost:5433/investmentdb` |
| `TEST_MODE` | Use SQLite for testing instead of PostgreSQL | `false` |
| `JWT_SECRET_KEY` | Secret key for JWT token generation | `your-secret-key` (dev only) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | `30` |

### API Documentation

The project uses OpenAPI (formerly Swagger) specifications to document all APIs. The specifications are automatically generated and updated in the CI/CD pipeline.

#### Consolidated API Documentation
A consolidated OpenAPI specification that includes all microservices is available at `docs/openapi.yaml`. This is the recommended specification for:
- Generating client code
- API documentation tools
- Overall API exploration

#### Individual Service Documentation
Each microservice also has its own OpenAPI specification in its docs directory (e.g., `services/investment-service/docs/openapi.yaml`). These are useful for:
- Service-specific documentation
- Local development
- Individual service client generation

To view the API documentation:
1. Use the consolidated spec at `docs/openapi.yaml` for a complete view of all APIs
2. Or navigate to individual service specs in `services/<service-name>/docs/openapi.yaml`
3. Use an OpenAPI viewer like [Swagger Editor](https://editor.swagger.io/) to view the documentation

To generate the OpenAPI specifications locally:

```bash
python scripts/generate_openapi.py
```

This will create or update both the consolidated spec and individual service specs.

### Development Workflow

1. Activate your virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. Install services in editable mode (if not already done):
   ```bash
   cd services/user-service && pip install -e . && cd ../..
   cd services/investment-service && pip install -e . && cd ../..
   ```

3. Run the database (if using Docker):
   ```bash
   docker-compose up -d postgres
   ```

4. Run the monolith for development:
   ```bash
   ./run_monolith.sh
   ```

5. Make changes to code and test them immediately (hot reload is enabled)

6. Run tests to verify your changes:
   ```bash
   TEST_MODE=true ./run_tests.sh
   ```

### Service Development

Each microservice uses modern Python packaging standards with `pyproject.toml`:

#### Key Benefits:
- **Editable installs**: Changes to source code are immediately reflected
- **Proper imports**: Services can import each other without path issues
- **Modern packaging**: Uses PEP 518 standards instead of legacy setup.py

#### Service Setup:
```bash
# Navigate to any service
cd services/service-name

# Install in editable mode
pip install -e .

# Verify installation
python3 -c "import service_name; print('OK')"
```

#### Python Compatibility:
- **Minimum version**: Python 3.9+
- **Avoid**: Python 3.11+ features like `from datetime import UTC`
- **Use**: `from datetime import timezone` and `timezone.utc` instead

### Continuous Integration

Our CI pipeline is configured with GitHub Actions. On each commit, tests are run automatically and the coverage report is uploaded to Codecov. You can view the workflow results [here](https://github.com/sri-akshat/wealth-manager/actions).

Additionally, OpenAPI specifications are automatically generated and committed to the repository whenever changes are pushed to the main branch. The consolidated spec is also available as a build artifact in the GitHub Actions workflow.

## Project Structure

```
wealth-manager/
├── services/                 # All microservices
│   ├── investment-service/   # Investment management service
│   ├── user-service/         # User management and authentication
│   ├── transaction-service/  # Transaction processing
│   ├── kyc-service/          # KYC verification
│   ├── admin-service/        # Admin dashboard functionality
│   └── notification-service/ # Notifications (email, SMS)
├── docs/                     # Documentation, including OpenAPI specs
├── scripts/                  # Utility scripts
├── docker-compose.yml        # Docker Compose configuration with PostgreSQL databases
├── run_tests.sh              # Script to run tests for all services
├── run_monolith.sh           # Script to run all services as a monolith
└── README.md                 # This file
```

## Contributing

Contributions are welcome! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.

## Troubleshooting

### Common Issues

#### Database Connection Errors
- Ensure PostgreSQL is running
- Verify DATABASE_URL environment variable is correct
- Check if the database exists
- **For Docker**: Ensure containers are running with `docker-compose ps`
- **For Docker**: Check container logs with `docker-compose logs user-db`
- **For Docker**: Verify database connectivity with `docker exec` commands

#### Import Errors When Running Monolith
- Ensure you're running from the project root
- Verify all dependencies are installed
- Check that __init__.py files exist in module directories
- **Install services in editable mode**: `pip install -e .` in each service directory
- **Verify imports**: `python3 -c "import service_name; print('OK')"`

#### Module Import Errors
- **Problem**: `ModuleNotFoundError: No module named 'service_name'`
- **Solution**: Install the service in editable mode:
  ```bash
  cd services/service-name
  pip install -e .
  ```

#### Python Version Compatibility Issues
- **Problem**: Using Python 3.11+ features in Python 3.9
- **Common Issues**:
  - `from datetime import UTC` (use `from datetime import timezone` and `timezone.utc`)
  - `from typing import Self` (not available in Python 3.9)
  - `match`/`case` statements (not available in Python 3.9)
- **Solution**: Always test with Python 3.9 and use compatible syntax

#### Dependency Conflicts
- **Problem**: Package installation fails or conflicts
- **Solution**: 
  1. Upgrade pip: `python3 -m pip install --upgrade pip`
  2. Use editable installs: `pip install -e .`
  3. Check dependencies: `pip check`

#### Test Failures
- Use TEST_MODE=true to run tests with SQLite
- Ensure you have the latest code changes
- Verify environment variables are set correctly
- **Check service installation**: `pip list | grep service-name`
- **Verify editable installs**: Services should show paths to source directories

#### Docker Issues
- **Containers not starting**: Check Docker Desktop is running
- **Port conflicts**: Ensure ports 5432 and 5433 are available
- **Database connection refused**: Wait for containers to fully start (check logs)
- **Permission errors**: Ensure Docker has proper permissions
- **Container cleanup**: Use `docker-compose down -v` to remove volumes if needed