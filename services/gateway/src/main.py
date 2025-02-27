# services/gateway/src/main.py
from fastapi import FastAPI

app = FastAPI(title="API Gateway")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gateway"}
