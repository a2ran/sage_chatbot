from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
import uvicorn
import os
from dotenv import load_dotenv

from app.api import chat_router
from app.models import HealthResponse
from app.config import settings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"SAGE Chatbot API starting up...")
    print(f"Environment: {settings.ENVIRONMENT}")
    yield
    print("SAGE Chatbot API shutting down...")

app = FastAPI(
    title="SAGE Chatbot API",
    description="노년층을 위한 AI 도우미 챗봇 서비스",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(
        status="healthy",
        message="SAGE Chatbot API is running",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development"
    )