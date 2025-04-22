from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import os
import mimetypes
from app.services.ocr_service import process_pdf, process_image, process_text
from app.core.config import settings

router = APIRouter(tags=["OCR"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (PDF or image) for OCR processing.
    
    Returns the file ID for further processing.
    """
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Get file extension and check if it's supported
    file_ext = os.path.splitext(file.filename)[1].lower()
    content_type = file.content_type
    
    if file_ext not in ['.pdf', '.png', '.jpg', '.jpeg'] and not (
        content_type and content_type in ['application/pdf', 'image/png', 'image/jpeg']
    ):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    
    # Return success response with filename for further processing
    return {
        "success": True,
        "filename": file.filename,
        "content_type": content_type,
        "size": file_size
    }

@router.post("/extract")
async def extract_text(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Extract text from a file or direct text input.
    
    Returns the extracted text in markdown format.
    """
    if file is None and text is None:
        raise HTTPException(status_code=400, detail="Either file or text must be provided")
    
    if file:
        # Process file based on content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        if content_type == 'application/pdf' or file.filename.lower().endswith('.pdf'):
            result = await process_pdf(file.file, file.filename)
        elif content_type in ['image/png', 'image/jpeg'] or any(file.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg']):
            result = await process_image(file.file, file.filename)
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type")
    else:
        # Process text input
        result = await process_text(text)
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
    
    return result

@router.post("/convert")
async def convert_to_markdown(text: str = Form(...)):
    """
    Convert text to markdown format.
    
    Returns the converted markdown.
    """
    result = await process_text(text)
    
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Conversion failed"))
    
    return result
