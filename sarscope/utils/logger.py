"""
Custom logging setup for SarScope.
Provides colored console output and file logging.
"""

import logging
import logging.handlers
import sys
from typing import Optional

from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console output."""
    
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        if record.levelno in self.COLORS:
            record.levelname = self.COLORS[record.levelno] + levelname + Style.RESET_ALL
        return super().format(record)


class SarScopeLogger:
    """Custom logger for SarScope application."""
    
    _instance: Optional["SarScopeLogger"] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> "SarScopeLogger":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize logger."""
        if self._logger is None:
            self._logger = self._setup_logger()
    
    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Set up logger with console and file handlers."""
        logger = logging.getLogger("sarscope")
        logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler with colored output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        try:
            from config import LOG_FILE
            file_handler = logging.FileHandler(LOG_FILE)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
        
        return logger
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        return self._logger
    
    @staticmethod
    def debug(message: str) -> None:
        """Log debug message."""
        logger = SarScopeLogger()._logger
        logger.debug(message)
    
    @staticmethod
    def info(message: str) -> None:
        """Log info message."""
        logger = SarScopeLogger()._logger
        logger.info(message)
    
    @staticmethod
    def warning(message: str) -> None:
        """Log warning message."""
        logger = SarScopeLogger()._logger
        logger.warning(message)
    
    @staticmethod
    def error(message: str) -> None:
        """Log error message."""
        logger = SarScopeLogger()._logger
        logger.error(message)
    
    @staticmethod
    def critical(message: str) -> None:
        """Log critical message."""
        logger = SarScopeLogger()._logger
        logger.critical(message)


# Create module-level logger instance
logger = SarScopeLogger().get_logger()
