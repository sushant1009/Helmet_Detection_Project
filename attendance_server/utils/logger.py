import logging
import sys
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from config import LOG_LEVEL, CLEAR_LOGS_ON_STARTUP

def setup_logger(name: str = "Attendance_Server", log_level: str = "INFO"):
    
   
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    # Fixed app name
    if os.path.exists("/app/logs"):
        log_dir = Path("/app/logs")  # Docker
    else:
        log_dir = Path(__file__).parent.parent / "logs"  # Local
        
    if CLEAR_LOGS_ON_STARTUP and name == "Attendance_Server":
        clear_all_logs(log_dir)
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)
    
    
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File Handler - All logs
    try:
        file_handler = RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # File Handler - Errors only
        error_handler = RotatingFileHandler(
            filename=log_dir / "errors.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        

        
    except PermissionError as e:
        logger.addHandler(console_handler)
    
    return logger

def clear_all_logs(log_dir: Path):
    """Delete all log files on startup"""
    try:
        if not log_dir.exists():
            return
        
        # Delete all .log files
        for log_file in log_dir.glob("*.log*"):
            if log_file.is_file():
                log_file.unlink()
                print(f"  Deleted: {log_file.name}")
        
        print(f"All logs cleared")
        
    except Exception as e:
        print(f" Error clearing logs: {e}")



logger = setup_logger()