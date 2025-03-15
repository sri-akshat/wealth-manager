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
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


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
        
        # Extract response model and status code
        response_model = None
        status_code = 200
        responses = {}
        
        response_model_match = re.search(r'response_model\s*=\s*([^,\s)]+)', decorator_params)
        if response_model_match:
            response_model = response_model_match.group(1)
        
        # Handle both integer and HTTP status code constants
        status_code_match = re.search(r'status_code\s*=\s*([^,\s)]+)', decorator_params)
        if status_code_match:
            status_code_str = status_code_match.group(1)
            if status_code_str.isdigit():
                status_code = int(status_code_str)
            else:
                # Handle HTTP status code constants
                status_code_map = {
                    'HTTP_200_OK': 200,
                    'HTTP_201_CREATED': 201,
                    'HTTP_202_ACCEPTED': 202,
                    'HTTP_204_NO_CONTENT': 204,
                    'HTTP_400_BAD_REQUEST': 400,
                    'HTTP_401_UNAUTHORIZED': 401,
                    'HTTP_403_FORBIDDEN': 403,
                    'HTTP_404_NOT_FOUND': 404,
                    'HTTP_409_CONFLICT': 409,
                    'HTTP_422_UNPROCESSABLE_ENTITY': 422,
                    'HTTP_500_INTERNAL_SERVER_ERROR': 500,
                    'status.HTTP_200_OK': 200,
                    'status.HTTP_201_CREATED': 201,
                    'status.HTTP_202_ACCEPTED': 202,
                    'status.HTTP_204_NO_CONTENT': 204,
                    'status.HTTP_400_BAD_REQUEST': 400,
                    'status.HTTP_401_UNAUTHORIZED': 401,
                    'status.HTTP_403_FORBIDDEN': 403,
                    'status.HTTP_404_NOT_FOUND': 404,
                    'status.HTTP_409_CONFLICT': 409,
                    'status.HTTP_422_UNPROCESSABLE_ENTITY': 422,
                    'status.HTTP_500_INTERNAL_SERVER_ERROR': 500
                }
                status_code = status_code_map.get(status_code_str.split('.')[-1], 200)
        
        # Extract responses dictionary
        responses_match = re.search(r'responses\s*=\s*\{([^}]+)\}', decorator_params)
        if responses_match:
            responses_str = responses_match.group(1)
            for response_match in re.finditer(r'(\d+):\s*\{\s*"model":\s*([^,}]+)', responses_str):
                status = int(response_match.group(1))
                model = response_match.group(2)
                description = re.search(r'"description":\s*"([^"]+)"', responses_str)
                responses[status] = {
                    "model": model,
                    "description": description.group(1) if description else "Response"
                }
        
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
                
                # Extract function parameters
                params_str = content[func_def_start+4:func_end].strip()
                params_match = re.search(r'\((.*)\)', params_str)
                params = []
                if params_match:
                    params_list = params_match.group(1).split(',')
                    for param in params_list:
                        param = param.strip()
                        if param and ':' in param:
                            name, type_hint = param.split(':')
                            name = name.strip()
                            type_hint = type_hint.split('=')[0].strip()
                            params.append({
                                'name': name,
                                'type': type_hint
                            })
                
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
                    'tags': tags,
                    'response_model': response_model,
                    'status_code': status_code,
                    'responses': responses,
                    'parameters': params
                })
    
    return {
        'params': app_params,
        'endpoints': endpoints
    }


def extract_schema_info(schema_path: Path) -> Dict[str, Any]:
    """Extract schema information from a Pydantic model file."""
    content = schema_path.read_text()
    schemas = {}
    
    # Extract class definitions
    class_pattern = r'class\s+(\w+)\(.*?\):\s*(?:"""(.*?)""")?'
    for match in re.finditer(class_pattern, content, re.DOTALL):
        class_name = match.group(1)
        docstring = match.group(2).strip() if match.group(2) else ""
        
        # Extract fields
        fields = {}
        field_pattern = r'(\w+):\s*([^=\n]+)(?:\s*=\s*Field\(([^)]+)\))?'
        class_content = content[match.end():].split("class")[0]
        
        for field_match in re.finditer(field_pattern, class_content):
            field_name = field_match.group(1)
            field_type = field_match.group(2).strip()
            field_params = field_match.group(3) if field_match.group(3) else ""
            
            field_info = {"type": "string"}  # Default type
            
            # Map Python types to OpenAPI types
            type_mapping = {
                "str": "string",
                "int": "integer",
                "float": "number",
                "bool": "boolean",
                "List": "array",
                "Dict": "object",
                "datetime": {"type": "string", "format": "date-time"},
                "EmailStr": {"type": "string", "format": "email"},
                "Optional": None  # Handle separately
            }
            
            # Handle Optional types
            if "Optional" in field_type:
                inner_type = re.search(r'Optional\[(.*?)\]', field_type).group(1)
                field_info["nullable"] = True
                field_type = inner_type
            
            # Map the type
            if field_type in type_mapping:
                if isinstance(type_mapping[field_type], dict):
                    field_info.update(type_mapping[field_type])
                else:
                    field_info["type"] = type_mapping[field_type]
            
            # Extract field metadata from Field()
            if field_params:
                if "description" in field_params:
                    desc_match = re.search(r'description="([^"]+)"', field_params)
                    if desc_match:
                        field_info["description"] = desc_match.group(1)
                
                if "min_length" in field_params:
                    min_match = re.search(r'min_length=(\d+)', field_params)
                    if min_match:
                        field_info["minLength"] = int(min_match.group(1))
            
            fields[field_name] = field_info
        
        schemas[class_name] = {
            "type": "object",
            "properties": fields,
            "description": docstring
        }
    
    return schemas


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
        "tags": params.get('tags', []),
        "components": {
            "schemas": {},
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
    
    # Process endpoints
    for endpoint in endpoints:
        path = endpoint['path']
        method = endpoint['method'].lower()
        
        if path not in openapi["paths"]:
            openapi["paths"][path] = {}
        
        operation = {
            "tags": endpoint['tags'],
            "summary": endpoint['description'].split('\n')[0] if endpoint['description'] else "",
            "description": endpoint['description'],
            "responses": {
                str(endpoint['status_code']): {
                    "description": "Successful response",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"#/components/schemas/{endpoint['response_model']}"
                            } if endpoint['response_model'] else {}
                        }
                    }
                }
            }
        }
        
        # Add error responses
        for status_code, response_info in endpoint['responses'].items():
            operation["responses"][str(status_code)] = {
                "description": response_info["description"],
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": f"#/components/schemas/{response_info['model']}"
                        }
                    }
                }
            }
        
        # Add parameters
        parameters = []
        for param in endpoint['parameters']:
            if param['name'] not in ['db', 'token']:  # Skip internal parameters
                param_info = {
                    "name": param['name'],
                    "in": "query" if param['name'] in ['skip', 'limit'] else "path",
                    "required": True,
                    "schema": {"type": "integer"} if param['name'] in ['skip', 'limit'] else {"type": "string"}
                }
                parameters.append(param_info)
        
        if parameters:
            operation["parameters"] = parameters
        
        # Add security requirement for protected endpoints
        if any(param['name'] == 'token' for param in endpoint['parameters']):
            operation["security"] = [{"bearerAuth": []}]
        
        openapi["paths"][path][method] = operation
    
    return openapi


def merge_openapi_specs(specs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple OpenAPI specs into one."""
    if not specs:
        return {}
    
    # Use the first spec as base
    merged = specs[0].copy()
    
    # Update info
    merged["info"]["title"] = "Wealth Manager API"
    merged["info"]["description"] = "Combined API documentation for all Wealth Manager services"
    
    # Merge paths and components from other specs
    for spec in specs[1:]:
        # Merge paths
        for path, path_item in spec["paths"].items():
            if path in merged["paths"]:
                merged["paths"][path].update(path_item)
            else:
                merged["paths"][path] = path_item
        
        # Merge components
        if "components" in spec:
            if "components" not in merged:
                merged["components"] = {}
            
            # Merge schemas
            if "schemas" in spec["components"]:
                if "schemas" not in merged["components"]:
                    merged["components"]["schemas"] = {}
                merged["components"]["schemas"].update(spec["components"]["schemas"])
            
            # Merge security schemes
            if "securitySchemes" in spec["components"]:
                if "securitySchemes" not in merged["components"]:
                    merged["components"]["securitySchemes"] = {}
                merged["components"]["securitySchemes"].update(spec["components"]["securitySchemes"])
    
    return merged


def find_services() -> List[Dict[str, Any]]:
    """Find all services in the project."""
    services = []
    services_dir = Path("services")
    
    if not services_dir.exists():
        print("Services directory not found")
        return []
    
    # Known service names and their package names
    service_mapping = {
        "user-service": "user_service",
        "investment-service": "investment_service",
        "kyc-service": "kyc_service",
        "admin-service": "admin_service",
        "notification-service": "notification_service",
        "transaction-service": "transaction_service",
        "gateway": "gateway"
    }
    
    for service_dir in services_dir.iterdir():
        if not service_dir.is_dir():
            continue
        
        service_name = service_dir.name
        package_name = service_mapping.get(service_name, service_name.replace("-", "_"))
        
        # Try different possible locations for main.py
        possible_main_paths = [
            service_dir / "src" / package_name / "main.py",  # services/user-service/src/user_service/main.py
            service_dir / "src" / package_name / package_name / "main.py",  # services/user-service/src/user_service/user_service/main.py
            service_dir / "src" / "main.py",  # services/service-name/src/main.py
        ]
        
        main_py = None
        for path in possible_main_paths:
            if path.exists():
                main_py = path
                break
        
        if main_py:
            services.append({
                "name": service_name,
                "package_name": package_name,
                "service_dir": service_dir.absolute(),
                "main_py": main_py,
                "docs_dir": service_dir.absolute() / "docs"
            })
    
    return services


def generate_openapi(service_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Generate OpenAPI spec for a service."""
    try:
        main_py = service_info["main_py"]
        service_name = service_info["name"]
        package_name = service_info["package_name"]
        
        # Find schemas directory
        schemas_dir = main_py.parent / "schemas"
        if not schemas_dir.exists():
            schemas_dir = main_py.parent.parent / "schemas"
        
        # Extract app info from main.py
        app_info = extract_fastapi_app_info(main_py)
        if not app_info:
            return None
        
        # Generate basic OpenAPI spec with service-specific base path
        base_path = f"/{service_name.replace('_', '-')}"
        openapi = generate_basic_openapi(app_info, service_name, base_path)
        
        # Add schemas from schema files
        if schemas_dir.exists():
            for schema_file in schemas_dir.glob("*.py"):
                if schema_file.name != "__init__.py":
                    schemas = extract_schema_info(schema_file)
                    openapi["components"]["schemas"].update(schemas)
        
        return openapi
    
    except Exception as e:
        print(f"Error generating OpenAPI spec for {service_name}: {e}")
        return None


def generate_default_spec(service_name: str) -> Dict[str, Any]:
    """Generate a default OpenAPI specification for a service that doesn't have a FastAPI app yet."""
    return {
        'openapi': '3.0.0',
        'info': {
            'title': f'{service_name} API',
            'version': '1.0.0',
            'description': f'API specification for {service_name}'
        },
        'paths': {
            '/': {
                'get': {
                    'tags': ['system'],
                    'summary': 'Root endpoint that provides basic service information.',
                    'description': 'Returns service name, version, and status.',
                    'responses': {
                        '200': {
                            'description': 'Successful response',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'service': {'type': 'string'},
                                            'version': {'type': 'string'},
                                            'status': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            '/health': {
                'get': {
                    'tags': ['system'],
                    'summary': 'Health check endpoint.',
                    'description': 'Check if the service is healthy.',
                    'responses': {
                        '200': {
                            'description': 'Service is healthy',
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'status': {'type': 'string'}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        'tags': [
            {
                'name': 'system',
                'description': 'System maintenance operations'
            }
        ]
    }


def process_service(service_dir: Path) -> Optional[Dict[str, Any]]:
    """Process a service directory and generate its OpenAPI specification."""
    service_name = service_dir.name
    src_dir = service_dir / "src"
    if not src_dir.exists():
        print(f"No src directory found for {service_name}")
        return generate_default_spec(service_name)

    service_module_dir = src_dir / service_name.replace("-", "_")
    if not service_module_dir.exists():
        print(f"No service module directory found for {service_name}")
        return generate_default_spec(service_name)

    main_py = service_module_dir / "main.py"
    if not main_py.exists():
        print(f"No main.py found for {service_name}")
        return generate_default_spec(service_name)

    app_info = extract_fastapi_app_info(main_py)
    if not app_info:
        print(f"Could not extract FastAPI app info for {service_name}")
        return generate_default_spec(service_name)

    # Extract schemas from all Python files in the schemas directory
    schemas_dir = service_module_dir / "schemas"
    schemas = {}
    if schemas_dir.exists():
        for schema_file in schemas_dir.glob("*.py"):
            if schema_file.name != "__init__.py":
                schemas.update(extract_schema_info(schema_file))

    # Build OpenAPI spec
    spec = {
        'openapi': '3.0.0',
        'info': {
            'title': app_info['params'].get('title', f'{service_name} API'),
            'version': app_info['params'].get('version', '1.0.0'),
            'description': app_info['params'].get('description', f'API specification for {service_name}')
        },
        'paths': {},
        'tags': app_info['params'].get('tags', [
            {
                'name': 'system',
                'description': 'System maintenance operations'
            }
        ])
    }

    # Add root endpoint if not present
    if '/' not in spec['paths']:
        spec['paths']['/'] = {
            'get': {
                'tags': ['system'],
                'summary': 'Root endpoint that provides basic service information.',
                'description': 'Returns service name, version, and status.',
                'responses': {
                    '200': {
                        'description': 'Successful response',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'service': {'type': 'string'},
                                        'version': {'type': 'string'},
                                        'status': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    # Add health endpoint if not present
    if '/health' not in spec['paths']:
        spec['paths']['/health'] = {
            'get': {
                'tags': ['system'],
                'summary': 'Health check endpoint.',
                'description': 'Check if the service is healthy.',
                'responses': {
                    '200': {
                        'description': 'Service is healthy',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'status': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    # Process endpoints from app_info
    for endpoint in app_info['endpoints']:
        path = endpoint['path']
        method = endpoint['method'].lower()
        
        if path not in spec['paths']:
            spec['paths'][path] = {}
        
        operation = {
            'tags': endpoint['tags'],
            'summary': endpoint['description'].split('\n')[0] if endpoint['description'] else '',
            'description': endpoint['description'] or '',
            'responses': {}
        }

        # Add default 200 response if none specified
        if not endpoint['responses']:
            operation['responses']['200'] = {
                'description': 'Successful response',
                'content': {
                    'application/json': {
                        'schema': {}
                    }
                }
            }
        else:
            for status_code, response_info in endpoint['responses'].items():
                operation['responses'][str(status_code)] = {
                    'description': response_info['description'],
                    'content': {
                        'application/json': {
                            'schema': {
                                '$ref': f'#/components/schemas/{response_info["model"]}'
                            } if response_info.get('model') else {}
                        }
                    }
                }

        spec['paths'][path][method] = operation

    # Add components section if we have schemas
    if schemas:
        spec['components'] = {
            'schemas': schemas,
            'securitySchemes': {
                'bearerAuth': {
                    'type': 'http',
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        }

    return spec


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
        spec = process_service(service['service_dir'])
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