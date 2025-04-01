import logging
import sys
from datetime import datetime

def setup_logger():
    """Configure logging for the application"""
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(f'checkers_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    # Create formatters
    c_format = logging.Formatter('%(levelname)s: %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatters to handlers
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    # Add handlers to logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
