import logging
import sys

def get_logger(name="ulockai"):
    """
    Configures and returns a production-ready logger for the SDK.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Default to stdout for containerized/cloud environments
        handler = logging.StreamHandler(sys.stdout)
        
        # Standard production logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Default level
        logger.setLevel(logging.INFO)
        
    return logger

# Shared logger instance
logger = get_logger()
