"""
Multi-modal API endpoints for Xionimus AI
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import logging
import uuid
from typing import Optional

from ..core.multimodal import MultiModalProcessor

router = APIRouter(prefix="/api/multimodal", tags=["multimodal"])
logger = logging.getLogger(__name__)

# Temporary storage for uploaded files
TEMP_DIR = Path("~/.xionimus_ai/temp_uploads").expanduser()
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats for multi-modal"""
    return MultiModalProcessor.get_supported_formats()

@router.get("/vision-models")
async def get_vision_models():
    """Get list of AI models that support vision"""
    return {
        "vision_models": list(MultiModalProcessor.VISION_MODELS),
        "description": "Models that can process images"
    }

@router.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    Process an image file for AI vision models
    
    Returns:
        Image metadata and processing status
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save temporarily
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename or 'image.jpg').suffix
        temp_path = TEMP_DIR / f"{file_id}{file_ext}"
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Process image
        result = MultiModalProcessor.process_image(str(temp_path))
        
        # Clean up
        temp_path.unlink()
        
        return {
            "status": "success",
            "file_id": file_id,
            "original_filename": file.filename,
            "metadata": {
                "width": result['width'],
                "height": result['height'],
                "size_bytes": result['size_bytes'],
                "format": result['format']
            },
            "message": "Image processed successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")

@router.post("/process-pdf")
async def process_pdf(
    file: UploadFile = File(...),
    max_pages: int = Form(20)
):
    """
    Extract text from PDF file
    
    Args:
        file: PDF file
        max_pages: Maximum pages to process
        
    Returns:
        PDF text content and metadata
    """
    try:
        # Validate file type
        if not file.content_type or 'pdf' not in file.content_type.lower():
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Save temporarily
        file_id = str(uuid.uuid4())
        temp_path = TEMP_DIR / f"{file_id}.pdf"
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Process PDF
        result = MultiModalProcessor.process_pdf(str(temp_path), max_pages=max_pages)
        
        # Clean up
        temp_path.unlink()
        
        return {
            "status": "success",
            "file_id": file_id,
            "original_filename": file.filename,
            "metadata": result['metadata'],
            "pages_processed": result['pages_processed'],
            "total_pages": result['total_pages'],
            "char_count": result['char_count'],
            "text_preview": result['text'][:500] + "..." if len(result['text']) > 500 else result['text'],
            "full_text_available": True
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to process PDF")

@router.post("/validate-file")
async def validate_file(file: UploadFile = File(...)):
    """
    Validate if file can be processed for multi-modal
    
    Returns:
        Validation result
    """
    try:
        # Save temporarily
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename or 'file').suffix
        temp_path = TEMP_DIR / f"{file_id}{file_ext}"
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Validate
        validation = MultiModalProcessor.validate_file(str(temp_path))
        
        # Clean up
        temp_path.unlink()
        
        if validation['valid']:
            return {
                "valid": True,
                "file_type": validation['type'],
                "format": validation['format'],
                "message": f"File can be processed as {validation['type']}"
            }
        else:
            return {
                "valid": False,
                "error": validation['error'],
                "supported_formats": validation.get('supported')
            }
        
    except Exception as e:
        logger.error(f"Error validating file: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate file")
