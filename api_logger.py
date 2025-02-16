import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path

class LoggerFactory:
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize loggers
        self.conn_logger = self._setup_logger("commitly_connection", "connection.log")
        self.op_logger = self._setup_logger("commitly_operations", "operations.log")
    
    def _setup_logger(self, name, log_file):
        """Setup a specific logger with given name and file"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate logging
        if not logger.handlers:
            # Create formatters
            file_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            
            # File handler (with rotation)
            file_handler = logging.handlers.RotatingFileHandler(
                self.logs_dir / log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(console_formatter)
            
            # Add handlers to logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger

class StructuredLogger:
    """A wrapper around the standard logger that handles structured logging"""
    def __init__(self, logger):
        self._logger = logger

    def debug(self, message, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)

    def _log_with_context(self, level, message, **kwargs):
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self._logger.log(level, message)

class APILogger:
    def __init__(self):
        factory = LoggerFactory()
        self.conn = StructuredLogger(factory.conn_logger)  # Connection logger for API calls
        self.op = StructuredLogger(factory.op_logger)     # Operations logger for data processing
    
    def debug(self, message, **kwargs):
        """Log debug message to operations logger by default"""
        self.op.debug(message, **kwargs)
    
    def info(self, message, **kwargs):
        """Log info message to operations logger by default"""
        self.op.info(message, **kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message to operations logger by default"""
        self.op.warning(message, **kwargs)
    
    def error(self, message, **kwargs):
        """Log error message to operations logger by default"""
        self.op.error(message, **kwargs)

# Create a singleton instance
logger = APILogger()
