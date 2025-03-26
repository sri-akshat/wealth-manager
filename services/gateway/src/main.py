# services/gateway/src/main.py
from fastapi import FastAPI
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str
    service: str
    version: str
    status: str

app = FastAPI(
    title="Gateway Service",
    description="API Gateway service for wealth manager platform.",
    version="1.0.0",
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

@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint that provides basic service information."""
    return MessageResponse(
        message="Gateway Service API",
        service="Gateway Service",
        version="1.0.0",
        status="healthy"
    )

@app.get("/health", response_model=MessageResponse)
async def health_check():
    """Check if the service is healthy."""
    return MessageResponse(
        message="Service is operational",
        service="Gateway Service",
        version="1.0.0",
        status="healthy"
    )
