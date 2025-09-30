"""
Secure File Upload Validation
Prevents malicious file uploads and path traversal attacks
"""
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Set, Optional
import magic
import uuid
import os
import logging
import hashlib

logger = logging.getLogger(__name__)

# Allowed file extensions and MIME types
ALLOWED_EXTENSIONS: Set[str] = {
    # Documents
    '.pdf', '.txt', '.md', '.doc', '.docx',
    # Images
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
    # Code
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json', '.xml',
    # Archives (be careful!)
    '.zip',
}

ALLOWED_MIME_TYPES: Set[str] = {
    # Documents
    'application/pdf',
    'text/plain',
    'text/markdown',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    # Images
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    # Code/Text
    'text/x-python',
    'application/javascript',
    'application/json',
    'text/html',
    'text/css',
    'application/xml',
    'text/xml',
    # Archives
    'application/zip',
}

# Dangerous extensions that should NEVER be allowed
DANGEROUS_EXTENSIONS: Set[str] = {
    '.exe', '.dll', '.so', '.dylib',
    '.sh', '.bash', '.bat', '.cmd',
    '.app', '.deb', '.rpm',
    '.msi', '.pkg',
    '.scr', '.vbs', '.jar',
}

# Size limits
MAX_FILE_SIZE = 250 * 1024 * 1024  # 250MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB for images
MAX_TEXT_SIZE = 5 * 1024 * 1024     # 5MB for text files

class FileValidationError(HTTPException):
    """Raised when file validation fails"""
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks
    
    Returns: Safe filename with only alphanumeric, dots, underscores, hyphens
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
    sanitized = ''.join(c if c in safe_chars else '_' for c in filename)
    
    # Prevent hidden files
    if sanitized.startswith('.'):
        sanitized = '_' + sanitized[1:]
    
    # Ensure we have a filename
    if not sanitized or sanitized == '_':
        sanitized = 'unnamed_file'
    
    # Limit length
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized

def validate_file_extension(filename: str) -> str:
    """Validate file extension"""
    ext = Path(filename).suffix.lower()
    
    # Check for dangerous extensions
    if ext in DANGEROUS_EXTENSIONS:
        raise FileValidationError(
            f"Dangerous file type not allowed: {ext}"
        )
    
    # Check if extension is allowed
    if ext not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File type not allowed: {ext}. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    
    return ext

def validate_mime_type(content: bytes, expected_ext: str) -> str:
    """
    Validate MIME type using python-magic
    Prevents extension spoofing (e.g., malware.exe renamed to malware.pdf)
    """
    try:
        mime = magic.from_buffer(content, mime=True)
        
        # Check if MIME type is allowed
        if mime not in ALLOWED_MIME_TYPES:
            raise FileValidationError(
                f"MIME type not allowed: {mime}"
            )
        
        # Verify MIME type matches extension
        mime_ext_map = {
            'application/pdf': {'.pdf'},
            'image/png': {'.png'},
            'image/jpeg': {'.jpg', '.jpeg'},
            'text/plain': {'.txt', '.md'},
        }
        
        expected_mimes = mime_ext_map.get(expected_ext)
        if expected_mimes and mime not in expected_mimes:
            logger.warning(
                f"MIME type mismatch: extension {expected_ext} but MIME is {mime}"
            )
        
        return mime
        
    except Exception as e:
        logger.error(f"MIME type detection failed: {e}")
        raise FileValidationError("Unable to validate file type")

def validate_file_size(content: bytes, mime_type: str) -> None:
    """Validate file size based on type"""
    size = len(content)
    
    # Apply size limits based on type
    if mime_type.startswith('image/'):
        max_size = MAX_IMAGE_SIZE
    elif mime_type.startswith('text/'):
        max_size = MAX_TEXT_SIZE
    else:
        max_size = MAX_FILE_SIZE
    
    if size > max_size:
        raise FileValidationError(
            f"File too large: {size / (1024**2):.1f}MB. "
            f"Maximum: {max_size / (1024**2):.0f}MB"
        )
    
    if size == 0:
        raise FileValidationError("Empty file not allowed")

def scan_for_malware(content: bytes) -> None:
    """
    Basic malware detection (patterns-based)
    For production, integrate with ClamAV or similar
    """
    # Check for common malware signatures
    dangerous_patterns = [
        b'MZ\x90\x00',  # PE executable header
        b'\x7fELF',      # ELF executable header
        b'<script',      # Embedded scripts in uploads
        b'<?php',        # PHP code
    ]
    
    for pattern in dangerous_patterns:
        if pattern in content[:1024]:  # Check first 1KB
            raise FileValidationError(
                "File contains suspicious content"
            )

def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(content).hexdigest()

async def validate_upload(
    file: UploadFile,
    user_id: str,
    allowed_extensions: Optional[Set[str]] = None
) -> tuple[bytes, str, str]:
    """
    Comprehensive file upload validation
    
    Returns:
        (content, safe_filename, file_hash)
    
    Raises:
        FileValidationError: If validation fails
    """
    # Use custom allowed extensions if provided
    if allowed_extensions:
        global ALLOWED_EXTENSIONS
        original_allowed = ALLOWED_EXTENSIONS
        ALLOWED_EXTENSIONS = allowed_extensions
    
    try:
        # 1. Validate and sanitize filename
        safe_filename = sanitize_filename(file.filename)
        
        # 2. Validate extension
        ext = validate_file_extension(safe_filename)
        
        # 3. Read content
        content = await file.read()
        
        # 4. Validate MIME type (prevents extension spoofing)
        mime_type = validate_mime_type(content, ext)
        
        # 5. Validate size
        validate_file_size(content, mime_type)
        
        # 6. Scan for malware signatures
        scan_for_malware(content)
        
        # 7. Calculate hash for deduplication
        file_hash = calculate_file_hash(content)
        
        logger.info(
            f"File validated: {safe_filename} "
            f"({len(content) / 1024:.1f}KB, {mime_type})"
        )
        
        return content, safe_filename, file_hash
        
    finally:
        # Restore original allowed extensions
        if allowed_extensions:
            ALLOWED_EXTENSIONS = original_allowed

def generate_secure_path(
    user_id: str,
    filename: str,
    base_dir: str = "uploads"
) -> Path:
    """
    Generate secure file path with user isolation
    
    Structure: uploads/{user_id}/{uuid}_{filename}
    """
    # Create user-specific directory
    user_dir = Path(base_dir) / user_id
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to prevent overwrites
    unique_id = str(uuid.uuid4())[:8]
    secure_filename = f"{unique_id}_{filename}"
    
    full_path = user_dir / secure_filename
    
    # Double-check no path traversal
    if not str(full_path.resolve()).startswith(str(Path(base_dir).resolve())):
        raise FileValidationError("Invalid file path")
    
    return full_path

def save_file_securely(path: Path, content: bytes) -> None:
    """Save file with secure permissions"""
    # Write file
    with open(path, 'wb') as f:
        f.write(content)
    
    # Set secure permissions (owner read/write only)
    try:
        os.chmod(path, 0o600)
    except:
        logger.warning(f"Could not set file permissions for {path}")
