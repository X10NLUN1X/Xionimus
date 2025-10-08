"""
Application Constants
Centralized constants to replace magic numbers throughout the codebase
"""

# Timeout Constants (seconds)
DEFAULT_REQUEST_TIMEOUT = 30
SHORT_TIMEOUT = 10
LONG_TIMEOUT = 60
CODE_EXECUTION_TIMEOUT = 30
HEALTH_CHECK_TIMEOUT = 5

# File Size Limits (bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

# Memory Limits (MB)
PYTHON_MEMORY_LIMIT = 256
JAVASCRIPT_MEMORY_LIMIT = 512
BASH_MEMORY_LIMIT = 128
COMPILED_LANGUAGE_MEMORY_LIMIT = 512

# Rate Limiting
DEFAULT_RATE_LIMIT = 100  # requests per minute
AUTH_RATE_LIMIT = 5  # login attempts per minute
CHAT_RATE_LIMIT = 30  # chat requests per minute

# Cache TTL (seconds)
SHORT_CACHE_TTL = 60  # 1 minute
MEDIUM_CACHE_TTL = 300  # 5 minutes
LONG_CACHE_TTL = 3600  # 1 hour

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# JWT Token
JWT_EXPIRY_DAYS = 30
JWT_ALGORITHM = "HS256"  # For production, consider RS256

# Logging
LOG_MAX_LENGTH = 1000
LOG_RETENTION_DAYS = 30

# Service Names
SERVICES = ['backend', 'frontend', 'mongodb', 'code-server', 'mcp-server']

# API Versions
API_VERSION = "v1"
API_PREFIX = "/api"