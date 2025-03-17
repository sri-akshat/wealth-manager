# wealth-manager

[![Build Status](https://github.com/sri-akshat/wealth-manager/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/sri-akshat/wealth-manager/actions)
[![codecov](https://codecov.io/gh/sri-akshat/wealth-manager/graph/badge.svg?token=78ZRSI3PVO)](https://codecov.io/gh/sri-akshat/wealth-manager)

Scalable SaaS platform for Independent Financial Advisors (IFAs), AMCs, and financial distributors to manage customer investments, KYC compliance, and mutual fund transactions

## Getting Started

### Prerequisites

- Python 3.12.6
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
```

### Database Setup

#### Option 1: Using Docker (Recommended)

The project includes Docker Compose configuration for PostgreSQL:

```bash
# Start PostgreSQL container
docker-compose up -d postgres

# The database will be available at:
# - Host: localhost
# - Port: 5432
# - Username: postgres
# - Password: postgres
# - Default database: wealthdb
```

#### Option 2: Local PostgreSQL Installation

If you prefer to use a local PostgreSQL installation:

1. Install PostgreSQL on your system
2. Create a database for the project:

```bash
createdb wealthdb
```

3. Update the `.env` file with your PostgreSQL connection details:

```
DATABASE_URL=postgresql://username:password@localhost:5432/wealthdb
```

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
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/wealthdb` |
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

2. Run the database (if using Docker):
   ```bash
   docker-compose up -d postgres
   ```

3. Run the monolith for development:
   ```bash
   ./run_monolith.sh
   ```

4. Make changes to code and test them immediately (hot reload is enabled)

5. Run tests to verify your changes:
   ```bash
   TEST_MODE=true ./run_tests.sh
   ```

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
├── docker-compose.yml        # Docker Compose configuration
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

#### Import Errors When Running Monolith
- Ensure you're running from the project root
- Verify all dependencies are installed
- Check that __init__.py files exist in module directories

#### Test Failures
- Use TEST_MODE=true to run tests with SQLite
- Ensure you have the latest code changes
- Verify environment variables are set correctly