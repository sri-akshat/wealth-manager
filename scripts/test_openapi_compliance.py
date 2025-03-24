#!/usr/bin/env python3
"""
Test module to validate that FastAPI implementations match their OpenAPI specifications.
This ensures that the actual API behavior matches what is documented.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate_spec
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
import importlib.util
import sys
from datetime import datetime, date
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from fastapi import Depends
from investment_service.core.auth import oauth2_scheme

# Set test mode before importing modules
os.environ["TEST_MODE"] = "true"

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_openapi import find_services

# Import dependencies from investment service
from investment_service.models.investment import Base, MutualFund, Investment, FundCategory, InvestmentStatus
from investment_service.core.database import get_db, engine as test_engine
from investment_service.core.auth import get_current_user_id

def load_service_module(main_py_path: Path) -> Any:
    """Load a service module from its main.py file."""
    print(f"Loading module from {main_py_path}")
    
    # Add the service's src directory to Python path
    src_dir = main_py_path.parent
    while src_dir.name != "src" and src_dir.parent != src_dir:
        src_dir = src_dir.parent
    if src_dir.name == "src":
        print(f"Adding {src_dir} to Python path")
        sys.path.insert(0, str(src_dir))
    else:
        print(f"Could not find src directory for {main_py_path}")
        return None
    
    # Determine the module name from the path
    relative_path = main_py_path.relative_to(src_dir)
    module_parts = list(relative_path.parts)
    if module_parts[-1] == "__init__.py":
        module_parts.pop()
    elif module_parts[-1] == "main.py":
        module_parts[-1] = "main"
    module_name = ".".join(module_parts)
    
    print(f"Loading module {module_name}")
    try:
        # Try to import the module using importlib
        module = importlib.import_module(module_name)
        return module
    except Exception as e:
        print(f"Error loading module {module_name}: {e}")
        return None
    finally:
        # Remove the service's src directory from Python path
        if str(src_dir) in sys.path:
            sys.path.remove(str(src_dir))


def generate_example_value(schema: Dict[str, Any]) -> Any:
    """Generate an example value based on OpenAPI schema."""
    schema_type = schema.get("type", "string")
    schema_format = schema.get("format", None)
    
    if schema_type == "string":
        if schema_format == "date-time":
            return datetime.now().isoformat()
        elif schema_format == "date":
            return date.today().isoformat()
        elif schema_format == "email":
            return "test@example.com"
        elif schema_format == "password":
            return "password123"
        else:
            return "test_string"
    elif schema_type == "integer":
        return 42
    elif schema_type == "number":
        return 42.0
    elif schema_type == "boolean":
        return True
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        return [generate_example_value(items_schema)]
    elif schema_type == "object":
        if "properties" in schema:
            return {
                prop_name: generate_example_value(prop_schema)
                for prop_name, prop_schema in schema["properties"].items()
            }
        return {}
    return None


def generate_request_body(operation: dict) -> Optional[dict]:
    """Generate a request body based on the OpenAPI operation spec."""
    if "requestBody" not in operation:
        return None

    content = operation["requestBody"]["content"]
    
    # Handle application/x-www-form-urlencoded
    if "application/x-www-form-urlencoded" in content:
        schema = content["application/x-www-form-urlencoded"]["schema"]
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            if ref == "Body_login_token_post":
                return {
                    "username": "test@example.com",
                    "password": "password123",
                    "grant_type": "password"
                }
        return {}

    # Handle application/json
    if "application/json" in content:
        schema = content["application/json"]["schema"]
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            if ref == "InvestmentCreate":
                return {
                    "fund_id": 1,
                    "purchase_amount": 1000.0
                }
            elif ref == "UserCreate":
                return {
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "password": "password123"
                }
        return {}

    return {}


def resolve_schema_ref(spec: Dict[str, Any], ref: str) -> Dict[str, Any]:
    """Resolve a schema reference in the OpenAPI spec."""
    if not ref.startswith("#/"):
        raise ValueError(f"Only local references are supported: {ref}")
    
    parts = ref.split("/")[1:]  # Skip the '#'
    current = spec
    for part in parts:
        if part not in current:
            raise ValueError(f"Invalid reference: {ref}")
        current = current[part]
    
    return current


def validate_value_against_schema(value: Any, schema: Dict[str, Any], spec: Dict[str, Any], path: str = "") -> List[str]:
    """Validate a value against an OpenAPI schema."""
    errors = []
    
    # Resolve schema reference if needed
    if "$ref" in schema:
        schema = resolve_schema_ref(spec, schema["$ref"])
    
    # Get schema type
    schema_type = schema.get("type")
    if not schema_type:
        return [f"{path}: Schema type not specified"]
    
    # Check type
    if schema_type == "string":
        if not isinstance(value, str):
            errors.append(f"{path}: Expected string, got {type(value).__name__}")
        else:
            # Check format if specified
            schema_format = schema.get("format")
            if schema_format == "date-time":
                try:
                    datetime.fromisoformat(value.replace("Z", "+00:00"))
                except ValueError:
                    errors.append(f"{path}: Invalid date-time format")
            elif schema_format == "date":
                try:
                    date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{path}: Invalid date format")
            elif schema_format == "email":
                if "@" not in value:  # Simple email validation
                    errors.append(f"{path}: Invalid email format")
    
    elif schema_type == "number":
        if not isinstance(value, (int, float)):
            errors.append(f"{path}: Expected number, got {type(value).__name__}")
    
    elif schema_type == "integer":
        if not isinstance(value, int):
            errors.append(f"{path}: Expected integer, got {type(value).__name__}")
    
    elif schema_type == "boolean":
        if not isinstance(value, bool):
            errors.append(f"{path}: Expected boolean, got {type(value).__name__}")
    
    elif schema_type == "array":
        if not isinstance(value, list):
            errors.append(f"{path}: Expected array, got {type(value).__name__}")
        else:
            items_schema = schema.get("items", {})
            for i, item in enumerate(value):
                item_path = f"{path}[{i}]"
                errors.extend(validate_value_against_schema(item, items_schema, spec, item_path))
    
    elif schema_type == "object":
        if not isinstance(value, dict):
            errors.append(f"{path}: Expected object, got {type(value).__name__}")
        else:
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            # Check required properties
            for prop in required:
                if prop not in value:
                    errors.append(f"{path}: Missing required property '{prop}'")
            
            # Validate each property
            for prop_name, prop_value in value.items():
                if prop_name in properties:
                    prop_path = f"{path}.{prop_name}" if path else prop_name
                    errors.extend(validate_value_against_schema(
                        prop_value,
                        properties[prop_name],
                        spec,
                        prop_path
                    ))
                elif not schema.get("additionalProperties", True):
                    errors.append(f"{path}: Additional property '{prop_name}' not allowed")
    
    return errors


def validate_response(response: Any, expected_schema: Dict[str, Any], spec: Dict[str, Any]) -> List[str]:
    """Validate a response against its expected schema."""
    errors = []
    
    # Validate content type
    content = expected_schema.get("content", {})
    if "application/json" not in content:
        return ["Response schema does not specify application/json content"]
    
    # Get response schema
    schema = content["application/json"].get("schema", {})
    if not schema:
        return ["Response schema not specified"]
    
    try:
        response_data = response.json()
    except Exception as e:
        return [f"Failed to parse response as JSON: {e}"]
    
    # Validate response data against schema
    return validate_value_against_schema(response_data, schema, spec)


def test_openapi_spec_validity():
    """Test that all OpenAPI specifications are valid."""
    services = find_services()
    
    for service in services:
        spec_path = service["docs_dir"] / "openapi.yaml"
        if not spec_path.exists():
            pytest.skip(f"OpenAPI spec not found for {service['name']}")
        
        with open(spec_path) as f:
            spec = yaml.safe_load(f)
        
        try:
            validate_spec(spec)
        except OpenAPIValidationError as e:
            pytest.fail(f"Invalid OpenAPI spec for {service['name']}: {e}")


def mock_get_db():
    """Mock database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def mock_get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Mock function to return a test user ID."""
    return 1


def setup_test_data(module):
    """Set up test data and mocks for a service module."""
    # Create database tables
    if hasattr(module, "Base"):
        Base.metadata.create_all(bind=test_engine)

        # Create test session
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        db = TestingSessionLocal()

        # Add sample data if this is the investment service
        if hasattr(module, "MutualFund"):
            # Add a sample mutual fund
            fund = MutualFund(
                scheme_code="TEST001",
                scheme_name="Test Fund",
                category=FundCategory.EQUITY,
                nav=100.0,
                aum=1000000.0,
                risk_level="HIGH",
                expense_ratio=1.5
            )
            db.add(fund)
            db.commit()
            db.refresh(fund)

            # Add a sample investment
            investment = Investment(
                user_id="test_user_id",
                fund_id=fund.id,
                units=10.0,
                purchase_nav=100.0,
                current_nav=110.0,
                purchase_amount=1000.0,
                current_value=1100.0,
                status=InvestmentStatus.COMPLETED
            )
            db.add(investment)
            db.commit()

        db.close()

    # Override dependencies
    if hasattr(module, "app"):
        module.app.dependency_overrides[get_db] = mock_get_db
        module.app.dependency_overrides[get_current_user_id] = mock_get_current_user_id


@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    """Mock external dependencies."""
    def mock_external_request(*args, **kwargs):
        """Mock external HTTP requests."""
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.content = b"{}"
                self.text = "{}"
            async def json(self):
                return {}
            def raise_for_status(self):
                pass
        return MockResponse()
    
    monkeypatch.setattr("httpx.AsyncClient.get", mock_external_request)
    monkeypatch.setattr("httpx.AsyncClient.post", mock_external_request)
    
    # Mock environment variables
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("TEST_MODE", "true")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")


@pytest.mark.integration
def test_api_implementation_matches_spec(mock_dependencies):
    """Test that API implementations match their OpenAPI specifications."""
    services = find_services()
    
    for service in services:
        spec_path = service["docs_dir"] / "openapi.yaml"
        if not spec_path.exists():
            pytest.skip(f"OpenAPI spec not found for {service['name']}")
        
        # Load OpenAPI spec
        with open(spec_path) as f:
            spec = yaml.safe_load(f)
        
        # Load service module
        module = load_service_module(service["main_py"])
        if not module or not hasattr(module, "app"):
            pytest.skip(f"Could not load FastAPI app for {service['name']}")
        
        # Set up test data and mocks
        setup_test_data(module)
        
        # Create test client
        client = TestClient(module.app)
        
        # Test each endpoint
        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method == "parameters":  # Skip common parameters
                    continue
                
                # Generate request data
                params = {}
                headers = {}
                body = generate_request_body(operation)
                
                # Add authentication if required
                if "security" in operation:
                    headers["Authorization"] = "Bearer test_token"
                
                try:
                    # Make request
                    response = client.request(
                        method=method.upper(),
                        url=path,
                        params=params,
                        headers=headers,
                        json=body
                    )

                    # Print response details for debugging
                    print(f"\nResponse status: {response.status_code}")
                    print(f"Response body: {response.text}")

                    # Get expected response schema
                    status_code = str(response.status_code)
                    if status_code not in operation.get("responses", {}):
                        pytest.fail(
                            f"Unexpected status code {status_code} for {method.upper()} {path} "
                            f"in {service['name']}"
                        )
                    
                    expected_schema = operation["responses"][status_code]
                    
                    # Validate response
                    errors = validate_response(response, expected_schema, spec)
                    if errors:
                        pytest.fail(
                            f"Response validation failed for {method.upper()} {path} "
                            f"in {service['name']}:\n" + "\n".join(errors)
                        )
                
                except Exception as e:
                    pytest.fail(
                        f"Error testing {method.upper()} {path} in {service['name']}: {e}"
                    )


def main():
    """Run the tests."""
    # Add current directory to Python path
    sys.path.insert(0, str(Path.cwd()))
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    main() 