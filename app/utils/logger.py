"""
Backward compatibility module for logging.
All logging functionality has been consolidated to app.core.logging using loguru.
"""

from app.core.logging import logger, setup_logging

__all__ = ['logger', 'setup_logging']
