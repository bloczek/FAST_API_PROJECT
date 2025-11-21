import hmac
import logging
import os
import time
from functools import wraps
from typing import dict, list

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging with level from environment
log_level = os.getenv("MCP_LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Security settings from environment
MAX_REQUESTS = int(os.getenv("MCP_RATE_LIMIT", "100"))  # requests per minute
REQUEST_WINDOW = 60  # seconds
MAX_REQUEST_SIZE = int(os.getenv("MCP_MAX_REQUEST_SIZE", "1048576"))  # 1MB in bytes
API_KEY = os.getenv("MCP_API_KEY", "default-dev-key")  # In production, require this to be set

# Rate limiting state
request_history: dict[str, list[float]] = {}


def authenticate(func):
    """Authentication decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # In a real application, you would get these from the request context
        # For MCP, we'll use environment variables for demonstration
        api_key = os.getenv("MCP_CLIENT_API_KEY")

        if not api_key:
            logger.warning("No API key provided")
            return func(*args, **kwargs)  # Allow request in development

        if not hmac.compare_digest(api_key, API_KEY):
            msg = "Invalid API key"
            logger.error(msg)
            raise ValueError(msg)

        return func(*args, **kwargs)

    return wrapper


def rate_limit(func):
    """Rate limiting decorator."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        client_id = "default"  # In a real app, get this from authentication

        # Initialize or update request history
        if client_id not in request_history:
            request_history[client_id] = []

        # Clean old requests
        request_history[client_id] = [t for t in request_history[client_id] if current_time - t < REQUEST_WINDOW]

        # Check rate limit
        if len(request_history[client_id]) >= MAX_REQUESTS:
            msg = f"Rate limit exceeded. Maximum {MAX_REQUESTS} requests per {REQUEST_WINDOW} seconds"
            logger.warning(msg)
            raise ValueError(msg)

        # Add current request
        request_history[client_id].append(current_time)

        return func(*args, **kwargs)

    return wrapper


# Initialize the MCP server
mcp = FastMCP("Demo")


@mcp.tool()
@authenticate
@rate_limit
def add(a: int, b: int) -> int:
    """Add two numbers with input validation and rate limiting.

    Args:
        a: First number (must be within safe integer bounds)
        b: Second number (must be within safe integer bounds)

    Returns:
        Sum of the two numbers

    Raises:
        ValueError: If inputs are invalid or rate limit is exceeded
    """
    # Prevent integer overflow
    max_int = 2**31 - 1
    if not (-max_int <= a <= max_int) or not (-max_int <= b <= max_int):
        msg = f"Numbers must be between {-max_int} and {max_int}"
        logger.error(msg)
        raise ValueError(msg)

    result = a + b
    logger.info(f"Adding {a} + {b} = {result}")
    return result


def main():
    """Entry point for the MCP server."""
    logger.info("Starting MCP server...")
    mcp.run()
