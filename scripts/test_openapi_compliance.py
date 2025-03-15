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

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_openapi import find_services


def load_service_module(main_py_path: Path) -> Any:
    """Load a service module from its main.py file."""
    spec = importlib.util.spec_from_file_location("service_module", main_py_path)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules["service_module"] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module: {e}")
        return None


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


def generate_request_body(operation_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate a request body based on OpenAPI operation specification."""
    if "requestBody" not in operation_spec:
        return None
    
    content = operation_spec["requestBody"].get("content", {})
    if "application/json" not in content:
        return None
    
    schema = content["application/json"].get("schema", {})
    if "$ref" in schema:
        # TODO: Handle schema references
        return {}
    
    return generate_example_value(schema)


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


def setup_test_data(module: Any) -> None:
    """Set up test data for a service module."""
    # Mock database session if needed
    if hasattr(module, "get_db"):
        def get_test_db():
            # Return a mock or test database session
            return None
        module.get_db = get_test_db
    
    # Mock authentication if needed
    if hasattr(module, "get_current_user"):
        async def get_test_user():
            return {
                "id": 1,
                "email": "test@example.com",
                "full_name": "Test User",
                "role": "USER",
                "is_active": True
            }
        module.get_current_user = get_test_user
    
    # Mock external services if needed
    if hasattr(module, "get_external_service"):
        def get_test_external_service():
            return None
        module.get_external_service = get_test_external_service


@pytest.fixture
def mock_dependencies(monkeypatch):
    """Fixture to mock common dependencies."""
    # Mock database
    def mock_db_session():
        return None
    monkeypatch.setattr("sqlalchemy.orm.Session", mock_db_session)
    
    # Mock JWT verification
    def mock_verify_token():
        return {"sub": "test@example.com"}
    monkeypatch.setattr("jose.jwt.decode", mock_verify_token)
    
    # Mock external API calls
    def mock_external_request(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"status": "success"}
        return MockResponse()
    monkeypatch.setattr("httpx.AsyncClient.get", mock_external_request)
    monkeypatch.setattr("httpx.AsyncClient.post", mock_external_request)


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