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

# Function to import app from a service directory
def import_app_from_service(service_name: str):
    service_dir = services_dir / service_name
    src_dir = service_dir / "src"
    service_path = src_dir / "main.py"
    module_name = service_name.replace('-', '_')
    
    # Ensure all directories have __init__.py files
    ensure_init_files(service_dir)
    
    # Set up the module hierarchy with proper specs
    root_module = create_module(module_name, str(service_dir))
    sys.modules[module_name] = root_module
    
    src_module = create_module(f"{module_name}.src", str(src_dir))
    sys.modules[f"{module_name}.src"] = src_module
    
    # Import the main module
    spec = importlib.util.spec_from_file_location(
        f"{module_name}.src.main",
        service_path
    )
    module = importlib.util.module_from_spec(spec)
    module.__package__ = f"{module_name}.src"
    sys.modules[f"{module_name}.src.main"] = module
    
    # Add the src directory to sys.path temporarily
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    try:
        spec.loader.exec_module(module)
        return module.app
    finally:
        # Remove the src directory from sys.path
        if str(src_dir) in sys.path:
            sys.path.remove(str(src_dir))

# Import service applications
try:
    investment_app = import_app_from_service("investment-service")
    user_app = import_app_from_service("user-service")
    transaction_app = import_app_from_service("transaction-service")
    kyc_app = import_app_from_service("kyc-service")
    admin_app = import_app_from_service("admin-service")
    notification_app = import_app_from_service("notification-service")
except Exception as e:
    print(f"Error importing services: {str(e)}")
    raise

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
app.mount("/investments", investment_app)
app.mount("/users", user_app)
app.mount("/transactions", transaction_app)
app.mount("/kyc", kyc_app)
app.mount("/admin", admin_app)
app.mount("/notifications", notification_app)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "investment": "up",
            "user": "up",
            "transaction": "up",
            "kyc": "up",
            "admin": "up",
            "notification": "up"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 