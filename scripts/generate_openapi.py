#!/usr/bin/env python3
"""
Script to generate OpenAPI specification files for each service in the wealth-manager project.
This script uses a different approach that doesn't rely on importing existing FastAPI apps.
Instead, it extracts and rebuilds the routes manually.
"""

import os
import sys
import yaml
import json
import importlib.util
import inspect
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_module(file_path):
    """Load a Python module from a file path."""
    module_name = os.path.basename(file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        return None
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error loading module {module_name}: {e}")
        return None


def extract_fastapi_app_info(main_py_path: Path) -> Optional[Dict[str, Any]]:
    """Extract FastAPI app info from the main.py file."""
    content = main_py_path.read_text()
    
    # Extract app definition
    app_match = re.search(r'app\s*=\s*FastAPI\(\s*([^)]*)\)', content, re.DOTALL)
    if not app_match:
        print("Could not find FastAPI app definition")
        return None
    
    # Extract app initialization parameters
    app_params_str = app_match.group(1).strip()
    app_params = {}
    
    # Extract title
    title_match = re.search(r'title\s*=\s*["\']([^"\']*)["\']', app_params_str)
    if title_match:
        app_params['title'] = title_match.group(1)
    else:
        # Try to get title from settings
        settings_match = re.search(r'title\s*=\s*([^,\s]*)', app_params_str)
        if settings_match:
            settings_var = settings_match.group(1)
            settings_pattern = rf'{settings_var}\s*=\s*["\']([^"\']*)["\']'
            settings_value_match = re.search(settings_pattern, content)
            if settings_value_match:
                app_params['title'] = settings_value_match.group(1)
    
    # Extract version
    version_match = re.search(r'version\s*=\s*["\']([^"\']*)["\']', app_params_str)
    if version_match:
        app_params['version'] = version_match.group(1)
    
    # Extract description
    desc_match = re.search(r'description\s*=\s*["\']([^"\']*)["\']', app_params_str)
    if desc_match:
        app_params['description'] = desc_match.group(1)
    
    # Extract tags from openapi_tags
    tags_match = re.search(r'openapi_tags\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if tags_match:
        tags_str = tags_match.group(1)
        tags = []
        for tag_match in re.finditer(r'\{\s*"name":\s*"([^"]*)",\s*"description":\s*"([^"]*)"', tags_str):
            tags.append({
                "name": tag_match.group(1),
                "description": tag_match.group(2)
            })
        app_params['tags'] = tags
    
    # Extract endpoints
    endpoints = []
    route_pattern = r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']*)["\']([^)]*)\)'
    for match in re.finditer(route_pattern, content):
        method = match.group(1).upper()
        path = match.group(2)
        decorator_params = match.group(3)
        
        # Extract tags from decorator
        tags = []
        tags_match = re.search(r'tags=\[([^\]]*)\]', decorator_params)
        if tags_match:
            tags_str = tags_match.group(1)
            tags = [tag.strip(' "\'') for tag in tags_str.split(',')]
        
        # Find the function associated with this endpoint
        func_def_start = content.find("def ", match.end())
        if func_def_start != -1:
            func_end = content.find(":", func_def_start)
            if func_end != -1:
                func_name = content[func_def_start+4:func_end].strip().split("(")[0]
                
                # Extract docstring for function
                docstring_start = content.find('"""', func_end)
                if docstring_start != -1:
                    docstring_end = content.find('"""', docstring_start + 3)
                    if docstring_end != -1:
                        docstring = content[docstring_start+3:docstring_end].strip()
                    else:
                        docstring = None
                else:
                    docstring = None
                
                endpoints.append({
                    'method': method,
                    'path': path,
                    'function': func_name,
                    'description': docstring,
                    'tags': tags
                })
    
    return {
        'params': app_params,
        'endpoints': endpoints
    }


def generate_basic_openapi(app_info: Dict[str, Any], service_name: str, base_path: str) -> Dict[str, Any]:
    """Generate a basic OpenAPI specification."""
    params = app_info.get('params', {})
    endpoints = app_info.get('endpoints', [])
    
    openapi = {
        "openapi": "3.0.0",
        "info": {
            "title": params.get('title', f"{service_name} API"),
            "version": params.get('version', "1.0.0"),
            "description": params.get('description', f"API documentation for {service_name}")
        },
        "paths": {},
        "tags": params.get('tags', [])
    }
    
    # Add paths with service prefix
    for endpoint in endpoints:
        path = f"/{base_path}{endpoint['path']}"
        method = endpoint['method'].lower()
        
        if path not in openapi["paths"]:
            openapi["paths"][path] = {}
        
        openapi["paths"][path][method] = {
            "summary": endpoint['function'],
            "description": endpoint.get('description', ""),
            "tags": endpoint.get('tags', [service_name]),
            "responses": {
                "200": {
                    "description": "Successful Response"
                }
            }
        }
    
    return openapi


def merge_openapi_specs(specs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple OpenAPI specifications into one."""
    merged = {
        "openapi": "3.0.0",
        "info": {
            "title": "Wealth Manager API",
            "version": "1.0.0",
            "description": "Unified API documentation for the Wealth Manager platform"
        },
        "paths": {},
        "tags": []
    }
    
    # Track unique tags
    unique_tags = {}
    
    # Merge paths and tags from each spec
    for spec in specs:
        # Merge paths
        merged["paths"].update(spec.get("paths", {}))
        
        # Merge tags (avoiding duplicates)
        for tag in spec.get("tags", []):
            tag_name = tag["name"]
            if tag_name not in unique_tags:
                unique_tags[tag_name] = tag
    
    # Add unique tags to merged spec
    merged["tags"] = list(unique_tags.values())
    
    return merged


def generate_openapi(service_dir: Path, service_name: str) -> Optional[Dict[str, Any]]:
    """Generate OpenAPI spec for a service."""
    main_py_path = service_dir / "src" / "main.py"
    
    if not main_py_path.exists():
        print(f"main.py not found in {service_dir}/src")
        return None
    
    try:
        # Extract app info from main.py
        app_info = extract_fastapi_app_info(main_py_path)
        if not app_info:
            print(f"Could not extract FastAPI app info from {main_py_path}")
            return None
        
        # Generate basic OpenAPI spec with service-specific base path
        # Use the correct mount paths that match the main application
        service_mount_paths = {
            "user-service": "users",
            "investment-service": "investments",
            "transaction-service": "transactions",
            "kyc-service": "kyc",
            "admin-service": "admin",
            "notification-service": "notifications",
            "gateway": "gateway"
        }
        
        base_path = service_mount_paths.get(service_name, service_name.replace("-service", ""))
        openapi = generate_basic_openapi(app_info, service_name, base_path)
        
        return openapi
    except Exception as e:
        print(f"Error generating OpenAPI spec: {e}")
        return None


def find_services() -> List[Dict[str, Any]]:
    """Find all services in the project."""
    services = []
    services_dir = Path("services")
    
    if not services_dir.exists():
        print("Services directory not found")
        return []
    
    for service_dir in services_dir.iterdir():
        if not service_dir.is_dir():
            continue
        
        # Check if this is a service directory (contains src/main.py)
        main_py = service_dir / "src" / "main.py"
        if main_py.exists():
            services.append({
                "name": service_dir.name,
                "service_dir": service_dir.absolute(),
                "docs_dir": service_dir.absolute() / "docs"
            })
    
    return services


def main():
    """Main function to generate OpenAPI specs for all services."""
    services = find_services()
    
    if not services:
        print("No services found")
        return
    
    print(f"Found {len(services)} services")
    
    # Generate OpenAPI specs for each service
    specs = []
    for service in services:
        print(f"Processing {service['name']}...")
        
        # Generate OpenAPI spec
        spec = generate_openapi(service['service_dir'], service['name'])
        if spec:
            specs.append(spec)
            print(f"Successfully generated OpenAPI spec for {service['name']}")
            
            # Save individual service spec
            docs_dir = service['docs_dir']
            docs_dir.mkdir(exist_ok=True, parents=True)
            service_spec_path = docs_dir / "openapi.yaml"
            with open(service_spec_path, "w") as f:
                yaml.dump(spec, f, sort_keys=False)
        else:
            print(f"Failed to generate OpenAPI spec for {service['name']}")
    
    if specs:
        # Merge all specs into one
        merged_spec = merge_openapi_specs(specs)
        
        # Save merged spec to docs directory
        docs_dir = Path("docs")
        docs_dir.mkdir(exist_ok=True, parents=True)
        merged_spec_path = docs_dir / "openapi.yaml"
        with open(merged_spec_path, "w") as f:
            yaml.dump(merged_spec, f, sort_keys=False)
        print(f"\nGenerated consolidated OpenAPI specification at {merged_spec_path}")


if __name__ == "__main__":
    main() 