# wealth-manager

[![Build Status](https://github.com/sri-akshat/wealth-manager/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/sri-akshat/wealth-manager/actions)
[![codecov](https://codecov.io/gh/sri-akshat/wealth-manager/graph/badge.svg?token=78ZRSI3PVO)](https://codecov.io/gh/sri-akshat/wealth-manager)

Scalable SaaS platform for Independent Financial Advisors (IFAs), AMCs, and financial distributors to manage customer investments, KYC compliance, and mutual fund transactions

## Getting Started

### Prerequisites

- Python 3.12.6
- Git

### Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/sri-akshat/wealth-manager.git
cd wealth-manager
./project-setup.sh
find . -name "requirements.txt" -exec pip install -r {} \;
```

### Running Tests

This project uses pytest for its test suite and Codecov for test coverage reporting.

To run tests locally and generate a coverage report, use:

```bash
pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
```

This command will also generate a `coverage.xml` file which is uploaded to Codecov.

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

### Continuous Integration

Our CI pipeline is configured with GitHub Actions. On each commit, tests are run automatically and the coverage report is uploaded to Codecov. You can view the workflow results [here](https://github.com/sri-akshat/wealth-manager/actions).

Additionally, OpenAPI specifications are automatically generated and committed to the repository whenever changes are pushed to the main branch. The consolidated spec is also available as a build artifact in the GitHub Actions workflow.

## Contributing

Contributions are welcome! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.

To activate your virtual environment (.venv folder) and install the requirements, follow these steps:

For macOS (which you're using based on your system info):

1. Activate the virtual environment:
```
source .venv/bin/activate
```

You'll know it's activated when you see `(.venv)` at the beginning of your terminal prompt.

2. Install the root requirements:
```
pip install -r requirements.txt
```

3. Since your project has multiple services, you might want to install requirements for all services:
```
find . -name "requirements.txt" -exec pip install -r {} \;
```

This will find all requirements.txt files in your project structure and install the dependencies from each one.

If you need to deactivate the virtual environment later, simply type:
```
deactivate
```

Let me know if you have any issues with the installation!