import importlib.util
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import types

# Get the services directory path
services_dir = Path(__file__).parent

def ensure_init_files(directory: Path):
    """Create __init__.py files in all subdirectories."""
    if not directory.exists() or not directory.is_dir():
        return
        
    # Create __init__.py in current directory if it doesn't exist
    init_file = directory / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        
    # Recursively create __init__.py in subdirectories
    for item in directory.iterdir():
        if item.is_dir() and not item.name.startswith('.') and not item.name == '__pycache__':
            ensure_init_files(item)

def create_module(name: str, path: str) -> types.ModuleType:
    """Create a module with proper spec."""
    module = types.ModuleType(name)
    module.__file__ = path
    module.__path__ = [path]
    module.__package__ = name
    
    # Create and set the module spec
    spec = importlib.util.spec_from_file_location(name, path + "/__init__.py")
    module.__spec__ = spec
    
    return module

def import_app_from_service(service_name: str) -> FastAPI:
    """Import FastAPI app from a service, return dummy app if service doesn't exist."""
    module_name = service_name.replace('-', '_')
    service_dir = services_dir / service_name
    src_dir = service_dir / "src"
    service_path = src_dir / module_name / "main.py"
    
    # If service directory doesn't exist, return a dummy app
    if not service_dir.exists():
        dummy_app = FastAPI(title=f"{service_name} (Not Implemented)")
        @dummy_app.get("/")
        def service_not_implemented():
            return {"status": "not_implemented", "message": f"{service_name} is not implemented yet"}
        return dummy_app
    
    # Ensure all directories have __init__.py files
    ensure_init_files(service_dir)
    ensure_init_files(src_dir)
    ensure_init_files(src_dir / module_name)
    
    # Set up the module hierarchy with proper specs
    root_module = create_module(module_name, str(service_dir))
    sys.modules[module_name] = root_module
    
    src_module = create_module(f"{module_name}", str(src_dir / module_name))
    sys.modules[f"{module_name}"] = src_module
    
    # Import the main module
    spec = importlib.util.spec_from_file_location(
        f"{module_name}.main",
        service_path
    )
    if not spec or not spec.loader:
        dummy_app = FastAPI(title=f"{service_name} (Error)")
        @dummy_app.get("/")
        def service_error():
            return {"status": "error", "message": f"Could not load {service_name}"}
        return dummy_app
        
    module = importlib.util.module_from_spec(spec)
    module.__package__ = module_name
    sys.modules[f"{module_name}.main"] = module
    
    try:
        spec.loader.exec_module(module)
        return module.app
    except Exception as e:
        print(f"Error loading {service_name}: {str(e)}")
        dummy_app = FastAPI(title=f"{service_name} (Error)")
        @dummy_app.get("/")
        def service_error():
            return {"status": "error", "message": str(e)}
        return dummy_app

# Import service applications
service_apps = {}
for service_name in [
    "investment-service",
    "user-service",
    "transaction-service",
    "kyc-service",
    "admin-service",
    "notification-service"
]:
    try:
        service_apps[service_name] = import_app_from_service(service_name)
    except Exception as e:
        print(f"Error importing {service_name}: {str(e)}")
        dummy_app = FastAPI(title=f"{service_name} (Error)")
        @dummy_app.get("/")
        def service_error():
            return {"status": "error", "message": str(e)}
        service_apps[service_name] = dummy_app

app = FastAPI(
    title="Wealth Manager",
    description="Wealth Manager Platform - All Services",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount service applications
app.mount("/", service_apps["user-service"])
app.mount("/investments", service_apps["investment-service"])
app.mount("/transactions", service_apps["transaction-service"])
app.mount("/kyc", service_apps["kyc-service"])
app.mount("/admin", service_apps["admin-service"])
app.mount("/notifications", service_apps["notification-service"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "investment": "up" if "investment-service" in service_apps else "not_implemented",
            "user": "up" if "user-service" in service_apps else "not_implemented",
            "transaction": "up" if "transaction-service" in service_apps else "not_implemented",
            "kyc": "up" if "kyc-service" in service_apps else "not_implemented",
            "admin": "up" if "admin-service" in service_apps else "not_implemented",
            "notification": "up" if "notification-service" in service_apps else "not_implemented"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 