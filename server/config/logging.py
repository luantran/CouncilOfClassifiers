# config/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app=None):
    """
    Configure logging for the application

    Args:
        app: Flask app instance (optional, for Flask-specific logging)
    """
    # Determine log level from environment
    log_level = os.environ.get('LOG_LEVEL', 'DEBUG').upper()

    # Create logs directory if it doesn't exist
    log_dir = 'server/logs'
    os.makedirs(log_dir, exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Rotating file handler (max 10MB, keep 5 backups)
            RotatingFileHandler(
                os.path.join(log_dir, 'app.log'),
                maxBytes=10 * 1024 * 1024,
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )

    # Set specific log levels for noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('gensim').setLevel(logging.WARNING)

    # If Flask app provided, configure Flask logger
    if app:
        app.logger.setLevel(getattr(logging, log_level))

    logging.info("Logging configuration complete")