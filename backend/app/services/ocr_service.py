import base64
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
import tempfile
import os

from mistralai import Mistral
from mistralai import DocumentURLChunk, ImageURLChunk, TextChunk
from mistralai.models import OCRResponse

from app.core.config import settings

# Initialize Mistral client
client = Mistral(api_key=settings.MISTRAL_API_KEY)

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        # Replace image placeholders with actual images
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)

async def process_pdf(file: BinaryIO, filename: str) -> Dict:
    """
    Process a PDF file with OCR.
    
    Args:
        file: The uploaded file object
        filename: Name of the file
    
    Returns:
        Dictionary with OCR results
    """
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name
        
        # Upload file to Mistral's OCR service
        pdf_file = Path(temp_path)
        uploaded_file = client.files.upload(
            file={
                "file_name": filename,
                "content": pdf_file.read_bytes(),
            },
            purpose="ocr",
        )
        
        # Get URL for the uploaded file
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        # Process PDF with OCR, including embedded images
        pdf_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )
        
        # Get combined markdown
        markdown_content = get_combined_markdown(pdf_response)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "success": True,
            "markdown": markdown_content,
            "original_response": json.loads(pdf_response.model_dump_json())
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def process_image(file: BinaryIO, filename: str) -> Dict:
    """
    Process an image file with OCR.
    
    Args:
        file: The uploaded file object
        filename: Name of the file
    
    Returns:
        Dictionary with OCR results
    """
    try:
        # Create a temporary file to store the uploaded content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_path = temp_file.name
        
        # Read image and encode as base64
        image_file = Path(temp_path)
        encoded = base64.b64encode(image_file.read_bytes()).decode()
        base64_data_url = f"data:image/jpeg;base64,{encoded}"
        
        # Process image with OCR
        image_response = client.ocr.process(
            document=ImageURLChunk(image_url=base64_data_url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )
        
        # Get combined markdown
        markdown_content = get_combined_markdown(image_response)
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return {
            "success": True,
            "markdown": markdown_content,
            "original_response": json.loads(image_response.model_dump_json())
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

async def process_text(text: str) -> Dict:
    """
    Process text input and convert to markdown.
    
    Args:
        text: The input text
    
    Returns:
        Dictionary with processed text as markdown
    """
    try:
        # For text input, we'll use the Mistral chat model to convert to markdown
        chat_response = client.chat.complete(
            model="ministral-8b-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        TextChunk(
                            text=(
                                f"Convert the following text to well-formatted markdown, "
                                f"preserving structure like headings, lists, and tables:\n\n{text}"
                            )
                        ),
                    ],
                }
            ],
            temperature=0,
        )
        
        markdown_content = chat_response.choices[0].message.content
        
        return {
            "success": True,
            "markdown": markdown_content
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
