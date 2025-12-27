import math

import numpy as np
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class CEFRClassifier:
    def __init__(self, nb_service, doc2vec_service, bert_service):
        logger.info("Initializing CEFR Classifier...")
        self.models = {}

        self.nb_model = nb_service
        self.models['Naive Bayes'] = self.nb_model
        logger.debug("Added Naive Bayes model to ensemble")

        self.doc2vec_model = doc2vec_service
        self.models['Doc2Vec'] = self.doc2vec_model
        logger.debug("Added Doc2Vec model to ensemble")

        self.bert_model = bert_service
        self.models['BERT'] = self.bert_model
        logger.debug("Added BERT model to ensemble")

        logger.info(f"CEFR Classifier initialized with {len(self.models)} model(s)")

    def predict(self, text):
        """Orchestrate predictions from all models"""
        logger.info(f"Starting prediction for text (length: {len(text)} chars)")
        preds = {}

        # Call each model service (these can run in parallel)
        for model_name, model in self.models.items():
            logger.debug(f"Getting prediction from {model_name}...")
            try:
                pred_dict = model.predict(text)
                preds[model_name] = pred_dict
                logger.debug(f"{model_name} prediction: {pred_dict.get('prediction', 'N/A')}")
            except Exception as e:
                logger.error(f"Error getting prediction from {model_name}: {str(e)}", exc_info=True)
                raise

        # Aggregate results
        logger.debug("Aggregating predictions from all models...")
        result = self._aggregate_predictions(text, preds)

        logger.info(f"Prediction complete - Majority vote: {result['majority_vote']}, "
                    f"Confidence: {result['confidence']:.2f}")

        return result

    def _aggregate_predictions(self, text, preds):
        """Calculate ensemble metrics"""
        logger.debug(f"Aggregating predictions from {len(preds)} model(s)")

        predictions = {}
        probabilities = {}

        # Collect predictions
        for model_name, pred_dict in preds.items():
            predictions[model_name] = pred_dict['prediction']
            logger.debug(f"{model_name} prediction: {pred_dict['prediction']}")

        # Collect probabilities
        for model_name, pred_dict in preds.items():
            probabilities[model_name] = pred_dict['probabilities']
            logger.debug(f"{model_name} probabilities: {pred_dict['probabilities']}")

        # Calculate mean probabilities
        mean_probs = np.mean(
            np.array(list(probabilities.values())),
            axis=0
        )
        logger.debug(f"Mean probabilities: {mean_probs}")

        # Calculate majority vote
        votes = predictions.values()
        vote_counts = Counter(votes)
        majority_vote = vote_counts.most_common(1)[0][0]
        confidence = vote_counts.most_common(1)[0][1] / len(self.models)
        agreement_count = vote_counts.most_common(1)[0][1]
        threshold = math.ceil(len(self.models) / 2)

        use_majority_vote = agreement_count >= threshold


        mean_pred = int(np.argmax(mean_probs))
        mean_pred_proba = float(np.max(mean_probs))

        logger.debug(f"Vote counts: {dict(vote_counts)}")
        logger.debug(f"Majority vote: {majority_vote} with confidence {confidence:.2f}")
        logger.debug(f"Mean probabilities predictions: {mean_pred}")

        # Return aggregated results
        result = {
            'text': text,
            'predictions': predictions,
            'probabilities': probabilities,
            'use_majority_vote': use_majority_vote,
            'mean_probabilities': mean_probs.tolist(),
            'mean_pred': mean_pred,
            'mean_pred_proba': mean_pred_proba,
            'majority_vote': majority_vote,
            'confidence': confidence,
            'stats': {
                'num_models': len(self.models),
                'agreement_count': agreement_count,
                'all_agree': len(vote_counts) == 1
            }
        }

        logger.debug(f"Aggregation complete - All models agree: {result['stats']['all_agree']}")

        return result