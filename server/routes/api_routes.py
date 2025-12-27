from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ensemble-classifier'
    })


@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint for JSON API

    Request body:
    {
        "text": "Your text here"
    }

    Response:
    {
        "text": "Original text",
        "predictions": {...},
        "probabilities": {...},
        "majority_vote": 2,
        "mean_probabilities": [...],
        "confidence": 0.85,
        "stats": {...}
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400

        text = data['text'].strip()

        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400

        # Get prediction from ensemble service
        cefr_classifier = current_app.config['CEFR_CLASSIFIER']
        result = cefr_classifier.predict(text)

        logger.info(f"Prediction successful for text length: {len(text)}")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
