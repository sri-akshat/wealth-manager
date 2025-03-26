from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str
    service: str
    version: str
    status: str

app = FastAPI(
    title="Admin Service",
    description="Admin management service for wealth manager platform.",
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

@app.get("/health", response_model=MessageResponse, tags=["system"])
async def health_check():
    return MessageResponse(
        message="Service is operational",
        service="Admin Service",
        version="0.1.0",
        status="healthy"
    )

@app.get("/", response_model=MessageResponse, tags=["system"])
async def root():
    return MessageResponse(
        message="Admin Service API",
        service="Admin Service",
        version="0.1.0",
        status="healthy"
    )
