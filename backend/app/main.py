from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import os
from app.services.ocr_service import process_pdf, process_text
from app.core.config import settings

app = FastAPI(title="DoveAI OCR API", description="API for OCR processing using MistralAI")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Import and include API routes
from app.api.endpoints import ocr
app.include_router(ocr.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to DoveAI OCR API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7000, reload=True)
