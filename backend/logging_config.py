import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": f"logs/app_{datetime.now().strftime('%Y%m%d')}.json",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file", "json_file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": True,
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "fastapi": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging():
    """Set up logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG) 