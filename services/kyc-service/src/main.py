from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str
    service: str
    version: str
    status: str

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="KYC Service",
        version="0.1.0",
        description="KYC (Know Your Customer) service for wealth manager platform.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app = FastAPI(
    title="KYC Service",
    description="KYC (Know Your Customer) service for wealth manager platform.",
    version="0.1.0",
    contact={
        "name": "Wealth Manager Team",
        "url": "https://github.com/sri-akshat/wealth-manager",
    },
    license_info={
        "name": "Private",
    },
    openapi_tags=[
        {
            "name": "system",
            "description": "System maintenance operations",
        }
    ]
)

# Override the default OpenAPI schema
app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=MessageResponse)
async def health_check():
    return MessageResponse(
        message="Service is operational",
        service="KYC Service",
        version="0.1.0",
        status="healthy"
    )

@app.get("/", response_model=MessageResponse)
async def root():
    return MessageResponse(
        message="KYC Service API",
        service="KYC Service",
        version="0.1.0",
        status="healthy"
    )
