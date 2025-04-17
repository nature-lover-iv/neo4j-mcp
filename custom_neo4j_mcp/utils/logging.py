"""
Logging utilities for Neo4j MCP server.
"""
import os
import sys
import logging
from typing import Optional

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> logging.Logger:
    """
    Set up logging for the Neo4j MCP server.
    
    Args:
        level: Logging level (default: logging.INFO)
        log_file: Path to log file (default: None, logs to stdout)
        log_format: Log format string
        
    Returns:
        Logger instance
    """
    # Create logger
    logger = logging.getLogger("neo4j_mcp")
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)
    
    # File handler (if log_file is provided)
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        
    # Add handlers to logger
    for handler in handlers:
        logger.addHandler(handler)
        
    return logger
