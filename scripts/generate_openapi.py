#!/usr/bin/env python3
"""
Script to generate OpenAPI specification files for each service using FastAPI's built-in generation.
Uses minimal mocking to avoid actual database connections and external dependencies.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import yaml
import importlib
import unittest.mock
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import traceback
from unittest.mock import MagicMock

def mock_database():
    """Mock SQLAlchemy database connection."""
    # Mock SQLAlchemy engine and session
    mock_engine = MagicMock()
    mock_session = MagicMock()
    mock_session_maker = MagicMock(return_value=mock_session)

    # Mock database operations
    mock_engine.connect.return_value = MagicMock()
    mock_engine.raw_connection.return_value = MagicMock()
    mock_engine.begin.return_value = MagicMock()
    mock_engine.execute.return_value = MagicMock()
    mock_engine.scalar.return_value = MagicMock()

    # Mock session operations
    mock_session.commit.return_value = None
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.first.return_value = None
    mock_session.all.return_value = []

    # Create patches
    patches = [
        unittest.mock.patch("sqlalchemy.create_engine", return_value=mock_engine),
        unittest.mock.patch("sqlalchemy.orm.sessionmaker", return_value=mock_session_maker),
        unittest.mock.patch("sqlalchemy.orm.Session", mock_session.__class__),
    ]

    return patches

def find_services() -> List[Dict[str, Any]]:
    """Find all services in the workspace."""
    services_dir = Path("services")
    services = []

    # Find all service directories
    for service_dir in services_dir.iterdir():
        if not service_dir.is_dir() or service_dir.name == "shared":
            continue

        # Check if service uses package structure or flat structure
        src_dir = service_dir / "src"
        if not src_dir.exists():
            continue

        # Find main.py file
        main_py = None
        package_name = service_dir.name.replace("-", "_")
        possible_main_paths = [
            src_dir / package_name / "main.py",  # services/user-service/src/user_service/main.py
            src_dir / "main.py",  # services/service-name/src/main.py
        ]
        
        for path in possible_main_paths:
            if path.exists():
                main_py = path
                break

        if main_py:
            service = {
                "name": service_dir.name,
                "service_dir": str(service_dir),
                "has_package": (src_dir / package_name).exists(),
                "docs_dir": service_dir / "docs",  # Add docs directory path
                "main_py": main_py  # Add main.py path
            }
            services.append(service)

    print(f"Found {len(services)} services")
    return services


def setup_minimal_mocks():
    """Setup minimal mocks for external dependencies."""
    # Mock database session
    mock_session = unittest.mock.MagicMock()
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.first.return_value = None
    mock_session.all.return_value = []

    # Mock database engine and metadata
    mock_engine = unittest.mock.MagicMock()
    mock_metadata = unittest.mock.MagicMock()
    mock_metadata.create_all = unittest.mock.MagicMock()

    # Mock environment variables
    mock_env = {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "JWT_SECRET_KEY": "mock_secret",
        "JWT_ALGORITHM": "HS256",
        "REDIS_URL": "redis://localhost:6379",
        "SERVICE_PORT": "8000",
        "ADMIN_EMAIL": "admin@example.com",
        "ADMIN_PASSWORD": "admin123",
    }

    # Mock FastAPI security dependencies
    mock_user = unittest.mock.MagicMock()
    mock_user.id = "mock_user_id"
    mock_user.email = "user@example.com"
    mock_user.is_active = True

    # Create patches
    patches = [
        # Database related
        unittest.mock.patch("sqlalchemy.orm.session.Session", return_value=mock_session),
        unittest.mock.patch("sqlalchemy.create_engine", return_value=mock_engine),
        unittest.mock.patch("sqlalchemy.MetaData", return_value=mock_metadata),
        unittest.mock.patch("sqlalchemy.orm.sessionmaker", return_value=lambda: mock_session),
        
        # Environment variables
        unittest.mock.patch("os.getenv", mock_env.get),
        
        # FastAPI security
        unittest.mock.patch("fastapi.security.OAuth2PasswordBearer", return_value=lambda: "mock_token"),
        unittest.mock.patch("fastapi.Depends", return_value=lambda: mock_user),
    ]
    
    return patches


def patch_fastapi_dependencies():
    """Patch FastAPI's dependency handling to ignore SQLAlchemy Session and OAuth2 forms."""
    # Original functions from FastAPI
    original_get_dependant = importlib.import_module("fastapi.dependencies.utils").get_dependant
    original_analyze_param = importlib.import_module("fastapi.dependencies.utils").analyze_param
    original_create_response_field = importlib.import_module("fastapi.utils").create_response_field

    # Create a dummy dependency
    def dummy_dependency_fn():
        return None
    
    dummy_dependency = Depends(dummy_dependency_fn)

    def patched_get_dependant(*args, **kwargs):
        """Patched version that ignores problematic dependencies."""
        try:
            return original_get_dependant(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            # Handle both SQLAlchemy Session and OAuth2 form dependencies
            if ("sqlalchemy.orm.session.Session" in error_str or 
                "OAuth2PasswordRequestForm" in error_str):
                return None
            raise

    def patched_analyze_param(*args, **kwargs):
        """Patched version that handles problematic types."""
        try:
            return original_analyze_param(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            # Handle both SQLAlchemy models and OAuth2 forms
            if ("sqlalchemy" in error_str or 
                "OAuth2PasswordRequestForm" in error_str or
                "OAuth2PasswordBearer" in error_str):
                return None, dummy_dependency, None
            raise

    def patched_create_response_field(*args, **kwargs):
        """Patched version that handles problematic types."""
        try:
            return original_create_response_field(*args, **kwargs)
        except Exception as e:
            error_str = str(e)
            # Handle both SQLAlchemy models and OAuth2 forms
            if ("sqlalchemy" in error_str or 
                "OAuth2PasswordRequestForm" in error_str or
                "OAuth2PasswordBearer" in error_str):
                return None
            raise

    # Patch FastAPI's functions
    return [
        unittest.mock.patch(
            "fastapi.dependencies.utils.get_dependant",
            side_effect=patched_get_dependant
        ),
        unittest.mock.patch(
            "fastapi.dependencies.utils.analyze_param",
            side_effect=patched_analyze_param
        ),
        unittest.mock.patch(
            "fastapi.utils.create_response_field",
            side_effect=patched_create_response_field
        )
    ]


def generate_service_spec(service_dir: str, service_name: str, has_package: bool) -> None:
    """Generate OpenAPI spec for a service."""
    print(f"\nProcessing {service_name}...")
    
    # Add service source to Python path
    src_dir = os.path.join(service_dir, "src")
    sys.path.insert(0, src_dir)  # Insert at beginning to ensure our module is found first
    print(f"Added {src_dir} to Python path")

    # Import the main module
    if has_package:
        module_name = service_name.replace("-", "_") + ".main"
    else:
        module_name = "main"
    print(f"Importing {module_name}...")

    try:
        # Set up patches
        patches = []
        patches.extend(mock_database())
        patches.extend(patch_fastapi_dependencies())
        
        for patch in patches:
            patch.start()

        # Clear any existing module from sys.modules to prevent reuse
        if module_name in sys.modules:
            del sys.modules[module_name]
        if "main" in sys.modules:
            del sys.modules["main"]

        # Import the module
        module = importlib.import_module(module_name)
        
        # Get the FastAPI app instance
        app = module.app

        # Get OpenAPI spec
        openapi_spec = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags if hasattr(app, "openapi_tags") else None,
            servers=app.servers if hasattr(app, "servers") else None,
            terms_of_service=app.terms_of_service if hasattr(app, "terms_of_service") else None
        )

        # Add contact and license info if available
        if hasattr(app, "contact"):
            openapi_spec["info"]["contact"] = app.contact
        if hasattr(app, "license_info"):
            openapi_spec["info"]["license"] = app.license_info

        # Create docs directory if it doesn't exist
        docs_dir = os.path.join(service_dir, "docs")
        os.makedirs(docs_dir, exist_ok=True)

        # Save OpenAPI spec
        spec_path = os.path.join(docs_dir, "openapi.yaml")
        with open(spec_path, "w") as f:
            yaml.dump(openapi_spec, f, sort_keys=False)

        print(f"Successfully generated OpenAPI spec for {service_name}")

    except Exception as e:
        print(f"Error generating OpenAPI spec for {service_name}: {str(e)}")
        traceback.print_exc()

    finally:
        # Stop patches
        for patch in patches:
            patch.stop()

        # Remove service source from Python path
        if src_dir in sys.path:
            sys.path.remove(src_dir)

        # Clean up imported modules
        if module_name in sys.modules:
            del sys.modules[module_name]
        if "main" in sys.modules:
            del sys.modules["main"]


def main():
    """Main function."""
    services = find_services()
    
    # Generate OpenAPI specs for each service
    for service in services:
        generate_service_spec(service["service_dir"], service["name"], service["has_package"])


if __name__ == "__main__":
    main() 