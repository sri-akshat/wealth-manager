from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str
    service: str
    version: str
    status: str

app = FastAPI(
    title="Notification Service",
    description="Notification service for wealth manager platform.",
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
        service="Notification Service",
        version="0.1.0",
        status="healthy"
    )

@app.get("/", response_model=MessageResponse)
async def root():
    return MessageResponse(
        message="Notification Service API",
        service="Notification Service",
        version="0.1.0",
        status="healthy"
    )
