# Investment Service

Investment management service for wealth manager platform.

## Development Setup

### Prerequisites
- Python 3.9+
- pip 21.2.4+ (for editable installs with pyproject.toml)

### Installation
1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Install the service in editable mode:
   ```bash
   cd services/investment-service
   pip install -e .
   ```

### Running Tests
```bash
python3 -m pytest tests/ -v
```

## Dependencies

This service uses modern Python packaging standards with `pyproject.toml`. Key dependencies include:

- FastAPI >= 0.100.0
- SQLAlchemy >= 2.0.0
- Pydantic >= 2.7, < 3.0
- Python-Jose[cryptography] >= 3.3.0
- Python-multipart >= 0.0.6

## Notes

- The service is configured for Python 3.9+ compatibility
- All dependencies are properly pinned and compatible
- Uses modern setuptools configuration for editable installs
