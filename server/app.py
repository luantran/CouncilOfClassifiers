import os
from flask import Flask

# Use relative imports
from .config.logging import setup_logging
from .services.bert_service import BERTService
from .services.doc2vec_service import Doc2VecService
from flask_cors import CORS

setup_logging()

import logging
logger = logging.getLogger(__name__)

from .services.classifier import CEFRClassifier
from .services.model_loader import ModelLoader
from .routes.api_routes import api_bp
from .routes.web_routes import web_bp
from .services.nb_service import NaiveBayesService


def create_app():
    logger.info("Creating Flask application...")

    env = os.environ.get("FLASK_ENV", "production")
    is_dev = env == "development"

    # app = Flask(
    #     __name__,
    #     static_folder=None if is_dev else "../frontend/dist",
    #     static_url_path="/" if not is_dev else None
    # )

    # Create Flask app with conditional static folder
    if is_dev:
        # Development: No static folder (Vite serves frontend)
        app = Flask(__name__, static_folder=None)
        logger.info("Development mode: Frontend served by Vite")
    else:
        # Production: Serve React build from dist/
        app = Flask(
            __name__,
            static_folder="../frontend/dist",
            static_url_path=""
        )
        logger.info("Production mode: Serving frontend from dist/")

    # Enable CORS only in development
    if is_dev:
        CORS(app)
        logger.info("CORS enabled for development")

    # Force debug mode
    app.config['DEBUG'] = True

    # Add secret key for sessions
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    logger.debug("Secret key configured")

    # Load all models once at startup
    logger.info("Initializing ModelLoader...")
    model_loader = ModelLoader()
    model_loader.load_all_models()

    # Initialize services with loaded models
    logger.info("Initializing services...")
    nb_service = NaiveBayesService(model_loader)
    doc2vec_service = Doc2VecService(model_loader)
    bert_service = BERTService(model_loader)

    # Initialize ensemble service
    global cefr_classifier
    logger.info("Initializing CEFR classifier...")
    cefr_classifier = CEFRClassifier(nb_service, doc2vec_service, bert_service)
    app.config['CEFR_CLASSIFIER'] = cefr_classifier

    # Register routes
    logger.info("Registering blueprints...")
    app.register_blueprint(api_bp, url_prefix='/api')  # JSON API for React

    if not is_dev:
        # Only register web routes in production (to serve React)
        app.register_blueprint(web_bp)
        logger.info("Web routes registered for serving React build")


    logger.info("[OK] Flask application created successfully")
    return app


if __name__ == '__main__':
    logger.info("Starting Flask development server...")
    app = create_app()
    app.run(debug=True)