import logging
import os

def setup_logger(name):
    """
    Set up a logger with the specified name and configuration
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set log level from environment or default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(log_level)
    
    # Create console handler and set format
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger if it doesn't already have one
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger 