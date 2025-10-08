"""
Multi-modal support for Xionimus AI
Handles images and PDFs for AI vision models
"""

import base64
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class MultiModalProcessor:
    """Process images and PDFs for AI models"""
    
    # Supported image formats
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    
    # Supported document formats
    SUPPORTED_DOC_FORMATS = {'.pdf'}
    
    # Max image size for processing (to avoid memory issues)
    MAX_IMAGE_SIZE = (2048, 2048)
    
    # Vision-capable models
    VISION_MODELS = {
        'gpt-4o',
        'gpt-4-vision',
        'gpt-4-turbo',
        'claude-3-opus',
        'claude-3-sonnet',
        'claude-3-haiku',
        'claude-sonnet-4-5-20250929'
    }
    
    @classmethod
    def is_vision_model(cls, model: str) -> bool:
        """Check if model supports vision"""
        model_lower = model.lower()
        return any(vm in model_lower for vm in cls.VISION_MODELS)
    
    @classmethod
    def is_image(cls, file_path: str) -> bool:
        """Check if file is a supported image"""
        return Path(file_path).suffix.lower() in cls.SUPPORTED_IMAGE_FORMATS
    
    @classmethod
    def is_pdf(cls, file_path: str) -> bool:
        """Check if file is a PDF"""
        return Path(file_path).suffix.lower() in cls.SUPPORTED_DOC_FORMATS
    
    @classmethod
    def process_image(cls, file_path: str, resize: bool = True) -> Dict[str, Any]:
        """
        Process image file for AI vision models
        
        Args:
            file_path: Path to image file
            resize: Whether to resize large images
            
        Returns:
            Dict with image data and metadata
        """
        try:
            # Open and process image
            img = Image.open(file_path)
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if resize and (img.width > cls.MAX_IMAGE_SIZE[0] or img.height > cls.MAX_IMAGE_SIZE[1]):
                img.thumbnail(cls.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {img.size}")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return {
                'type': 'image',
                'format': 'jpeg',
                'data': img_base64,
                'width': img.width,
                'height': img.height,
                'size_bytes': len(buffer.getvalue()),
                'mime_type': 'image/jpeg'
            }
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    @classmethod
    def process_pdf(cls, file_path: str, max_pages: int = 20) -> Dict[str, Any]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            max_pages: Maximum pages to extract
            
        Returns:
            Dict with PDF text and metadata
        """
        try:
            reader = PdfReader(file_path)
            
            # Extract metadata
            metadata = {
                'num_pages': len(reader.pages),
                'title': reader.metadata.title if reader.metadata else None,
                'author': reader.metadata.author if reader.metadata else None
            }
            
            # Extract text from pages
            text_content = []
            pages_to_process = min(len(reader.pages), max_pages)
            
            for i in range(pages_to_process):
                page = reader.pages[i]
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {i+1} ---\n{text}")
            
            full_text = "\n\n".join(text_content)
            
            if len(reader.pages) > max_pages:
                full_text += f"\n\n[Note: PDF has {len(reader.pages)} pages, only first {max_pages} processed]"
            
            return {
                'type': 'pdf',
                'text': full_text,
                'metadata': metadata,
                'pages_processed': pages_to_process,
                'total_pages': len(reader.pages),
                'char_count': len(full_text)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    @classmethod
    def prepare_multimodal_message(
        cls,
        text: str,
        file_path: Optional[str] = None,
        provider: str = 'openai'
    ) -> List[Dict[str, Any]]:
        """
        Prepare message with text and optional image/PDF for AI model
        
        Args:
            text: User's text message
            file_path: Optional path to image or PDF
            provider: AI provider (openai, anthropic)
            
        Returns:
            Formatted message for the provider
        """
        if not file_path:
            # Text only
            return [{"role": "user", "content": text}]
        
        # Check file type
        if cls.is_image(file_path):
            # Image message
            img_data = cls.process_image(file_path)
            
            if provider == 'openai':
                # OpenAI format
                return [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{img_data['mime_type']};base64,{img_data['data']}"
                            }
                        }
                    ]
                }]
            elif provider == 'anthropic':
                # Anthropic format
                return [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": img_data['mime_type'],
                                "data": img_data['data']
                            }
                        }
                    ]
                }]
        
        elif cls.is_pdf(file_path):
            # PDF message - extract text and prepend to user message
            pdf_data = cls.process_pdf(file_path)
            
            combined_text = f"""[PDF Document: {Path(file_path).name}]
Pages: {pdf_data['pages_processed']}/{pdf_data['total_pages']}

Document Content:
{pdf_data['text']}

---

User Question: {text}"""
            
            return [{"role": "user", "content": combined_text}]
        
        else:
            # Unsupported file type
            logger.warning(f"Unsupported file type: {file_path}")
            return [{"role": "user", "content": text}]
    
    @classmethod
    def get_supported_formats(cls) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return {
            'images': list(cls.SUPPORTED_IMAGE_FORMATS),
            'documents': list(cls.SUPPORTED_DOC_FORMATS)
        }
    
    @classmethod
    def validate_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Validate if file can be processed
        
        Returns:
            Dict with validation result
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'valid': False, 'error': 'File does not exist'}
        
        if not path.is_file():
            return {'valid': False, 'error': 'Path is not a file'}
        
        suffix = path.suffix.lower()
        
        if suffix in cls.SUPPORTED_IMAGE_FORMATS:
            return {'valid': True, 'type': 'image', 'format': suffix}
        elif suffix in cls.SUPPORTED_DOC_FORMATS:
            return {'valid': True, 'type': 'pdf', 'format': suffix}
        else:
            return {
                'valid': False,
                'error': f'Unsupported format: {suffix}',
                'supported': cls.get_supported_formats()
            }
