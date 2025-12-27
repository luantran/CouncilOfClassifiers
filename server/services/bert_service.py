from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import numpy as np
from typing import Dict


class BERTService:
    """BERT classifier loaded locally (no API needed)."""

    def __init__(self, model_loader):
        """
        Initialize BERT service by loading model locally.
        """
        self.tokenizer = model_loader.bert_tokenizer
        self.model = model_loader.bert_model

        # Use GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def predict(self, text: str) -> Dict:
        """
        Get prediction from BERT model.

        Args:
            text: Input text to classify

        Returns:
            Dictionary with probabilities, predicted class, and label
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = F.softmax(outputs.logits, dim=-1)

        # Convert to numpy
        probs_array = probabilities[0].cpu().numpy()
        predicted_class = int(np.argmax(probs_array))

        return {
            'probabilities': probs_array.tolist(),
            'prediction': predicted_class,
        }