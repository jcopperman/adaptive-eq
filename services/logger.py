"""
Logging module for Adaptive EQ

This module provides consistent logging across all components of the application.
"""

import os
import logging
import sys
from datetime import datetime

# Set up log levels
LOG_LEVEL_MAP = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# Default log directory
DEFAULT_LOG_DIR = os.path.expanduser('~/.cache/adaptive-eq/logs')

def _ensure_log_directory(log_dir=None):
    """Ensure log directory exists"""
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def setup_logger(name, log_level='info', log_to_console=True, log_to_file=True, log_dir=None):
    """
    Set up a logger with console and/or file handlers.
    
    Args:
        name (str): Logger name, typically the module name (__name__)
        log_level (str): Logging level (debug, info, warning, error, critical)
        log_to_console (bool): Whether to log to console
        log_to_file (bool): Whether to log to file
        log_dir (str): Directory for log files, defaults to ~/.cache/adaptive-eq/logs
        
    Returns:
        logging.Logger: Configured logger
    """
    # Normalize log level
    log_level = log_level.lower()
    if log_level not in LOG_LEVEL_MAP:
        log_level = 'info'
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL_MAP[log_level])
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Add file handler
    if log_to_file:
        log_dir = _ensure_log_directory(log_dir)
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(log_dir, f'adaptive-eq_{today}.log')
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name=None, log_level=None):
    """
    Get a logger instance. If the logger already exists, it will be returned.
    Otherwise, a new logger will be created with default settings.
    
    Args:
        name (str): Logger name, defaults to root logger
        log_level (str): Override default log level
        
    Returns:
        logging.Logger: Logger instance
    """
    if name is None:
        name = 'adaptive-eq'
    
    logger = logging.getLogger(name)
    
    # If logger is not configured yet, configure it
    if not logger.handlers:
        # Check environment variable for log level
        env_log_level = os.environ.get('ADAPTIVE_EQ_LOG_LEVEL', '').lower()
        if env_log_level in LOG_LEVEL_MAP:
            level_to_use = env_log_level
        elif log_level in LOG_LEVEL_MAP:
            level_to_use = log_level
        else:
            level_to_use = 'info'
            
        logger = setup_logger(name, log_level=level_to_use)
    
    return logger

def log_exceptions(func):
    """
    Decorator to log exceptions raised by functions
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function that logs exceptions
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper
