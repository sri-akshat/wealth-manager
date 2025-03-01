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
find . -name "requirements.txt" -exec pip install -r {} \;
```

### Running Tests

This project uses pytest for its test suite and Codecov for test coverage reporting.

To run tests locally and generate a coverage report, use:

```bash
pytest --maxfail=1 --disable-warnings --cov=. --cov-report=xml
```

This command will also generate a `coverage.xml` file which is uploaded to Codecov.

### Continuous Integration

Our CI pipeline is configured with GitHub Actions. On each commit, tests are run automatically and the coverage report is uploaded to Codecov. You can view the workflow results [here](https://github.com/sri-akshat/wealth-manager/actions).

## Contributing

Contributions are welcome! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to the project.